# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import unittest

from instalooter.looters import ProfileLooter


USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")


class TestLogin(unittest.TestCase):

    @unittest.skipUnless(USERNAME and PASSWORD, "credentials required")
    def test_login(self):

        looter = ProfileLooter(USERNAME)

        self.assertFalse(looter.logged_in())
        self.assertRaises(RuntimeError, looter.medias)
        self.assertFalse(looter._cachefs.exists(looter._COOKIE_FILE))

        try:
            looter.login(USERNAME, PASSWORD)
            self.assertTrue(looter.logged_in())
            self.assertTrue(looter._cachefs.exists(looter._COOKIE_FILE))
            self.assertTrue(next(looter.medias()))
        finally:
            looter.logout()
            self.assertFalse(looter._cachefs.exists(looter._COOKIE_FILE))
