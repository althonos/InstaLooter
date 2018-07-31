# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import getpass
import logging

import verboselogs

from ..looters import InstaLooter


logger = verboselogs.VerboseLogger(__name__)


def login(args):
    if args['--username']:
        username = args['--username']
        if not InstaLooter._logged_in():
            password = args['--password'] or getpass.getpass()
            InstaLooter._login(username, password)
            if not args['--quiet']:
                logger.success('Logged in.')
        elif not args['--quiet']:
            logger.success("Already logged in.")
