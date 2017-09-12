# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import shutil
import tempfile
import unittest
import json

import instaLooter


class TestCLI(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_plain(self):
        instaLooter.main(["mysteryjets", self.tmpdir, "-q", '-n', '10'])
        self.assertEqual(len(os.listdir(self.tmpdir)), 10)

    def test_single_post(self):
        instaLooter.main(
            ["post", "https://www.instagram.com/p/BFB6znLg5s1/", self.tmpdir, "-q"]
        )
        self.assertIn("1243533605591030581.jpg", os.listdir(self.tmpdir))

        instaLooter.main(["post", "BIqZ8L8AHmH", self.tmpdir])
        self.assertIn("1308972728853756295.jpg", os.listdir(self.tmpdir))

    def test_dump_json(self):
        instaLooter.main(["post", "BIqZ8L8AHmH", self.tmpdir, '-q', '--dump-json'])
        self.assertIn("1308972728853756295.json", os.listdir(self.tmpdir))
        self.assertIn("1308972728853756295.jpg", os.listdir(self.tmpdir))
        with open(os.path.join(self.tmpdir, "1308972728853756295.json")) as fp:
            json_metadata = json.load(fp)
        self.assertEqual("1308972728853756295", json_metadata["id"])
        self.assertEqual("BIqZ8L8AHmH", json_metadata["code"])

    def test_dump_only(self):
        instaLooter.main(["post", "BIqZ8L8AHmH", self.tmpdir, '-q', '--dump-only'])
        self.assertIn("1308972728853756295.json", os.listdir(self.tmpdir))
        self.assertNotIn("1308972728853756295.jpg", os.listdir(self.tmpdir))
        with open(os.path.join(self.tmpdir, "1308972728853756295.json")) as fp:
            json_metadata = json.load(fp)
        self.assertEqual("1308972728853756295", json_metadata["id"])
        self.assertEqual("BIqZ8L8AHmH", json_metadata["code"])

    def test_fail_on_no_directory(self):
        self.assertTrue(instaLooter.main(
            ["post", "https://www.instagram.com/p/BFB6znLg5s1/", "-q"]
        ))
        self.assertTrue(instaLooter.main(
            ["hashtag", "anything", "-q"]
        ))
