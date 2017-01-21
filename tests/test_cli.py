import os
import shutil
import sys
import tempfile
import unittest
import warnings
import datetime

import instaLooter


class TestInstaLooterCommandLineInterface(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_cli_plain(self):
        instaLooter.main(["mysteryjets", self.tmpdir, "--get-videos", "-q"])
        self.assertGreaterEqual(len(os.listdir(self.tmpdir)), 686) # nb of post on 2016-12-21

    
