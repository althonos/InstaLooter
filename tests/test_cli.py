import os
import shutil
import tempfile
import unittest

import instaLooter


class TestInstaLooterCommandLineInterface(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_cli_plain(self):
        instaLooter.main(["mysteryjets", self.tmpdir, "--get-videos", "-q"])
        self.assertGreaterEqual(len(os.listdir(self.tmpdir)), 686) # nb of post on 2016-12-21

    def test_cli_single(self):
        instaLooter.main(
            ["post", "https://www.instagram.com/p/BFB6znLg5s1/", self.tmpdir, "-q"]
        )
        self.assertIn("1243533605591030581.jpg", os.listdir(self.tmpdir))

        instaLooter.main(["post", "BIqZ8L8AHmH", self.tmpdir])
        self.assertIn("1308972728853756295.jpg", os.listdir(self.tmpdir))

    def test_cli_no_directory_fail(self):
        self.assertTrue(
            ["post", "https://www.instagram.com/p/BFB6znLg5s1/", "-q"]
        )
        self.assertTrue(
            ["hashtag", "anything", "-q"]
        )
