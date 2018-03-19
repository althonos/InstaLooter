# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest
import json

import fs

import instaLooter.cli


class TestCLI(unittest.TestCase):

    def setUp(self):
        self.destfs = fs.open_fs("temp://")
        self.tmpdir = self.destfs.getsyspath("/")

    def tearDown(self):
        self.destfs.close()

    def test_plain(self):
        r =instaLooter.cli.main(["user", "mysteryjets", self.tmpdir, "-q", '-n', '10'])
        self.assertEqual(r, 0)
        self.assertEqual(len(self.destfs.listdir('/')), 10)

    def test_single_post(self):
        r = instaLooter.cli.main(["post", "BFB6znLg5s1", self.tmpdir, "-q"])
        self.assertEqual(r, 0)
        self.assertTrue(self.destfs.exists("1243533605591030581.jpg"))

    # def test_single_post_from_url(self):
    #     url = "https://www.instagram.com/p/BFB6znLg5s1/"
    #     instaLooter.cli.main(["post", url, self.tmpdir, "-q"])
    #     self.assertIn("1243533605591030581.jpg", os.listdir(self.tmpdir))

    def test_dump_json(self):
        instaLooter.cli.main(["post", "BIqZ8L8AHmH", self.tmpdir, '-q', '-d'])

        self.assertTrue(self.destfs.exists("1308972728853756295.json"))
        self.assertTrue(self.destfs.exists("1308972728853756295.jpg"))

        with self.destfs.open("1308972728853756295.json", "rb") as fp:
            json_metadata = json.load(fp)

        self.assertEqual("1308972728853756295", json_metadata["id"])
        self.assertEqual("BIqZ8L8AHmH", json_metadata["shortcode"])

    # def test_dump_only(self):
    #     instaLooter.cli.main(["post", "BIqZ8L8AHmH", self.tmpdir, '-q', '--dump-only'])
    #     self.assertIn("1308972728853756295.json", os.listdir(self.tmpdir))
    #     self.assertNotIn("1308972728853756295.jpg", os.listdir(self.tmpdir))
    #     with open(os.path.join(self.tmpdir, "1308972728853756295.json")) as fp:
    #         json_metadata = json.load(fp)
    #     self.assertEqual("1308972728853756295", json_metadata["id"])
    #     self.assertEqual("BIqZ8L8AHmH", json_metadata["code"])
    #
    # def test_fail_on_no_directory(self):
    #     self.assertTrue(instaLooter.cli.main(
    #         ["post", "https://www.instagram.com/p/BFB6znLg5s1/", "-q"]
    #     ))
    #     self.assertTrue(instaLooter.cli.main(
    #         ["hashtag", "anything", "-q"]
    #     ))
