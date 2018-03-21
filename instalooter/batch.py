# coding: utf-8
"""Run several jobs sharing a session using a configuration file.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import getpass
import logging
import os

import requests
import six

from .looters import HashtagLooter, InstaLooter, ProfileLooter
from .pbar import TqdmProgressBar

# mypy annotations
if False:
    import io
    from typing import Any, Dict, Type, Union


#: The module logger
logger = logging.getLogger(__name__)


class BatchRunner(object):
    """Run ``InstaLooter`` in batch mode, using a configuration file.
    """

    _CLS_MAP = {
        'users': ProfileLooter,
        'hashtag': HashtagLooter,
    }  # type: Dict[str, Type[InstaLooter]]

    def __init__(self,
                 handle,    # type: Any
                 args=None  # Dict[str, Any]
                 ):
        # type: (...) -> None

        close_handle = False
        if isinstance(handle, six.binary_type):
            handle = handle.decode('utf-8')
        if isinstance(handle, six.text_type):
            handle = open(handle)
            close_handle = True

        try:
            self.args = args or {}
            self.parser = six.moves.configparser.ConfigParser()
            getattr(self.parser, "readfp" if six.PY2 else "read_file")(handle)
        finally:
            if close_handle:
                handle.close()

    def _getboolean(self, section_id, key, default=None):
        if self.parser.has_option(section_id, key):
            return self.parser.getboolean(section_id, key)
        return default

    def _getint(self, section_id, key, default=None):
        if self.parser.has_option(section_id, key):
            return self.parser.getint(section_id, key)
        return default

    def _get(self, section_id, key, default=None):
        if self.parser.has_option(section_id, key):
            return self.parser.get(section_id, key)
        return default

    def runAll(self):
        """Run all the jobs specified in the configuration file.
        """

        logger.debug("Creating batch session")
        session = requests.Session()

        for section_id in self.parser.sections():
            self.runJob(section_id, session=session)

    def runJob(self, section_id, session=None):
        """Run a job as described in the section named ``section_id``.

        Raises:
            KeyError: when the section could not be found.

        """
        if not self.parser.has_section(section_id):
            raise KeyError('section not found: {}'.format(section_id))

        session = session or requests.Session()

        for name, looter_cls in six.iteritems(self._CLS_MAP):

            targets = self.getTargets(self._get(section_id, name))
            quiet = self._getboolean(
                section_id, "quiet", self.args.get("--quiet", False))

            if targets:
                logger.info("Launching {} job for section {}".format(name, section_id))

            for target, directory in six.iteritems(targets):

                logger.info("Downloading {} to {}".format(target, directory))
                looter = looter_cls(
                    target,
                    add_metadata=self._getboolean(section_id, 'add-metadata', False),
                    get_videos=self._getboolean(section_id, 'get-videos', False),
                    videos_only=self._getboolean(section_id, 'videos-only', False),
                    jobs=self._getint(section_id, 'jobs', 16),
                    template=self._get(section_id, 'template', '{id}'),
                    dump_json=self._getboolean(section_id, 'dump-json', False),
                    dump_only=self._getboolean(section_id, 'dump-only', False),
                    extended_dump=self._getboolean(section_id, 'extended-dump', False),
                    session=session)

                # if self.parser.has_option(section_id, 'username'):
                #     looter.logout()
                #     username = self._get(section_id, 'username')
                #     password = self._get(section_id, 'password') or \
                #         getpass.getpass('Password for "{}": '.format(username))
                #     looter.login(username, password)

                n = looter.download(
                    directory,
                    media_count=self._getint(section_id, 'num-to-dl'),
                    timeframe=self._get(section_id, 'timeframe'),
                    new_only=self._getboolean(section_id, 'new', False),
                    pgpbar_cls=None if quiet else TqdmProgressBar,
                    dlpbar_cls=None if quiet else TqdmProgressBar)

                logger.log(35, "Downloaded {} medias !".format(n))

    def getTargets(self, raw_string):
        """Extract targets from a string in 'key: value' format.
        """
        targets = {}
        if raw_string is not None:
            for line in raw_string.splitlines():
                if line:
                    target, directory = line.split(':', 1)
                    targets[target.strip()] = directory.strip()
        return targets
