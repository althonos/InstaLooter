import os
import shutil
import sys
import tempfile
import unittest
import warnings
import datetime

sys.path.insert(0,
    os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
)

import instaLooter


class TestInstaLooterCommandLineInterface(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_cli_plain(self):
        instaLooter.main(["mysteryjets", self.tmpdir, "--get-videos", "-q"])
        self.assertGreaterEqual(len(os.listdir(self.tmpdir)), 686) # nb of post on 2016-12-21

    def test_cli_nodirectory(self):
        """Issue #19 acceptance test
        """
        initial_dir = os.getcwd()
        os.chdir(self.tmpdir)
        instaLooter.main(["mysteryjets", "-n", "10", "-q"])
        self.assertEqual(len(os.listdir(self.tmpdir)), 10)
        os.chdir(initial_dir)

    def test_cli_template(self):
        """Issue #14 CLI acceptance test
        """
        instaLooter.main(["mysteryjets", self.tmpdir, "-n", "10", "-q", "-T", "{username}.{date}.{id}"])
        for f in os.listdir(self.tmpdir):
            self.assertTrue(f.startswith('mysteryjets'))
