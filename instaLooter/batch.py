# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import six
import getpass

from .core import InstaLooter


class BatchRunner(object):
    """Run `InstaLooter` in batch mode, using a configuration file.
    """

    def __init__(self, handle):
        self.parser = six.moves.configparser.ConfigParser()
        self.parser.readfp(handle) if six.PY2 else self.parser.read_file(handle)

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
        for section_id in self.parser.sections():
            self.runJob(section_id)

    def runJob(self, section_id):
        """Run a job as described in the section named `section_id`.

        Raises:
            KeyError: when the section could not be found.
        """

        if not self.parser.has_section(section_id):
            raise KeyError('section not found: {}'.format(section_id))

        for target_name in ('users', 'hashtags'):
            targets = self.getTargets(self._get(section_id, target_name))

            for target, directory in six.iteritems(targets):
                looter = InstaLooter(
                    directory=os.path.expanduser(directory),
                    profile=target if target_name=='users' else None,
                    hashtag=target if target_name=='hashtags' else None,
                    add_metadata=\
                        self._getboolean(section_id, 'add-metadata', False),
                    get_videos=\
                        self._getboolean(section_id, 'get-videos', False),
                    videos_only=\
                        self._getboolean(section_id, 'videos-only', False),
                    jobs=self._getint(section_id, 'jobs', 16),
                    template=self._get(section_id, 'template', '{id}'),
                    dump_json=self._getboolean(section_id, 'dump-json', False),
                    dump_only=self._getboolean(section_id, 'dump-only', False),
                    extended_dump=\
                        self._getboolean(section_id, 'extended-dump', False),
                    socks_port=self._getint(section_id, 'socks_port', None),
                    control_port=self._getint(section_id, 'control_port', None),
                    change_ip_after=self._getint(section_id, 'change_ip_after', 10),
                )
                
                try:
                    if self.parser.has_option(section_id, 'username'):
                        looter.logout()
                        username = self._get(section_id, 'username')
                        password = self._get(section_id, 'password') or \
                            getpass.getpass('Password for "{}": '.format(username))
                        looter.login(username, password)
                except Exception as ex:
                    print(ex)
                    continue
                
                try:
                    looter.download(
                        media_count=self._getint(section_id, 'num-to-dl'),
                        with_pbar=not self._getboolean(section_id, 'quiet', False),
                        new_only=self._getboolean(section_id, 'new', False),
                    )
                except Exception as ex:
                    print(ex)
                    continue

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
