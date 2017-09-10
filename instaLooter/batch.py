# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import six
import getpass
import configparser

from .core import InstaLooter


class BatchRunner(object):
    """Run `InstaLooter` in batch mode, using a configuration file.
    """

    def __init__(self, handle):
        self.parser = configparser.ConfigParser()
        self.parser.read_file(handle)

    def runAll(self):
        """Run all the jobs specified in the configuration file.
        """
        for section_id in six.iterkeys(self.parser):
            self.runJob(section_id)

    def runJob(self, section_id):
        """Run a job as described in the section named `section_id`.

        Raises:
            KeyError: when the section could not be found.
        """

        section = self.parser[section_id]

        for target_name in ('users', 'hashtags'):
            targets = self.getTargets(section.get(target_name))
            for target, directory in six.iteritems(targets):
                looter = InstaLooter(
                    directory=os.path.expanduser(directory),
                    profile=target if target_name=='users' else None,
                    hashtag=target if target_name=='hashtags' else None,
                    add_metadata=section.getboolean('add-metadata', False),
                    get_videos=section.getboolean('get_videos', False),
                    videos_only=section.getboolean('videos-only', False),
                    jobs=section.getint('jobs', 16),
                    template=section.get('template', '{id}'),
                )

                if 'username' in section:
                    looter.logout()
                    username = section.get('username')
                    password = section.get('password') or getpass.getpass(
                       'Password for "{}": '.format(username)
                    )
                    looter.login(username, password)

                looter.download(
                    media_count=section.getint('num-to-dl'),
                    with_pbar=not section.getboolean('quiet', False),
                    new_only=section.getboolean('new', False)
                )

    def getTargets(self, raw_string):
        """Extract targets from a string in 'key: value' format.
        """
        targets = {}
        if raw_string is not None:
            for line in raw_string.splitlines():
                if line:
                    target, directory = line.split(':')
                    targets[target.strip()] = directory.strip()
        return targets
