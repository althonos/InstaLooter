# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest
import json

import fs
import six

import instaLooter.cli
from instaLooter.cli._utils.constants import USAGE


class TestCLI(unittest.TestCase):

    def setUp(self):
        self.destfs = fs.open_fs("temp://")
        self.tmpdir = self.destfs.getsyspath("/")

    def tearDown(self):
        self.destfs.close()

    def test_user(self):
        r = instaLooter.cli.main(["user", "mysteryjets", self.tmpdir, "-q", '-n', '10'])
        self.assertEqual(r, 0)
        self.assertEqual(len(self.destfs.listdir('/')), 10)

    def test_single_post(self):
        r = instaLooter.cli.main(["post", "BFB6znLg5s1", self.tmpdir, "-q"])
        self.assertEqual(r, 0)
        self.assertTrue(self.destfs.exists("1243533605591030581.jpg"))

    def test_dump_json(self):
        r = instaLooter.cli.main(["post", "BIqZ8L8AHmH", self.tmpdir, '-q', '-d'])
        self.assertEqual(r, 0)

        self.assertTrue(self.destfs.exists("1308972728853756295.json"))
        self.assertTrue(self.destfs.exists("1308972728853756295.jpg"))

        with self.destfs.open("1308972728853756295.json") as fp:
            json_metadata = json.load(fp)

        self.assertEqual("1308972728853756295", json_metadata["id"])
        self.assertEqual("BIqZ8L8AHmH", json_metadata["shortcode"])

    def test_dump_only(self):
        r = instaLooter.cli.main(["post", "BIqZ8L8AHmH", self.tmpdir, '-q', '-D'])
        self.assertEqual(r, 0)

        self.assertTrue(self.destfs.exists("1308972728853756295.json"))
        self.assertFalse(self.destfs.exists("1308972728853756295.jpg"))

        with self.destfs.open("1308972728853756295.json") as fp:
            json_metadata = json.load(fp)

        self.assertEqual("1308972728853756295", json_metadata["id"])
        self.assertEqual("BIqZ8L8AHmH", json_metadata["shortcode"])

    def test_usage(self):
        handle = six.moves.StringIO()
        instaLooter.cli.main(["--usage"], stream=handle)
        self.assertEqual(handle.getvalue().strip(), USAGE.strip())

    @unittest.expectedFailure
    def test_single_post_from_url(self):
        url = "https://www.instagram.com/p/BFB6znLg5s1/"
        instaLooter.cli.main(["post", url, self.tmpdir, "-q"])
        self.assertIn("1243533605591030581.jpg", os.listdir(self.tmpdir))
