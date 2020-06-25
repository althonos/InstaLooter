# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import unittest

import requests
import fs.memoryfs

from instalooter.looters import InstaLooter, ProfileLooter


USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")

try:
    CONNECTION_FAILURE = not requests.get("https://instagr.am/instagram").ok
except requests.exceptions.ConnectionError:
    CONNECTION_FAILURE = True


@unittest.skipIf(os.getenv("CI") == "true", "not supported in CI")
@unittest.skipUnless(USERNAME and PASSWORD, "credentials required")
class TestLogin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()
        InstaLooter._user_agent = cls.session.headers["User-Agent"]

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        del InstaLooter._user_agent

    def setUp(self):
        self.looter = ProfileLooter(USERNAME, template="test")
        self.destfs = fs.memoryfs.MemoryFS()

    def tearDown(self):
        self.destfs.close()

    def test_login(self):

        self.assertFalse(self.looter.logged_in())
        self.assertRaises(RuntimeError, self.looter.medias)
        self.assertFalse(self.looter._cachefs.exists(self.looter._COOKIE_FILE))

        try:
            self.looter.login(USERNAME, PASSWORD)
            self.assertTrue(self.looter.logged_in())
            self.assertTrue(self.looter._cachefs.exists(self.looter._COOKIE_FILE))
            self.assertTrue(next(self.looter.medias()))
        finally:
            self.looter.logout()
            self.assertFalse(self.looter._cachefs.exists(self.looter._COOKIE_FILE))

    def test_download(self):
        try:
            self.looter.login(USERNAME, PASSWORD)
            self.looter.download(self.destfs)
            self.assertTrue(self.destfs.exists('test.jpg'))
            self.assertEqual(self.destfs.getbytes('test.jpg')[6:10], b'JFIF')
        finally:
            self.looter.logout()
