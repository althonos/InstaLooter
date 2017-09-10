# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import glob
import textwrap
import shutil
import unittest
import tempfile

from instaLooter.cli import main
from instaLooter.batch import BatchRunner



class TestBatchRunner(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_cli(self):

        cfg = textwrap.dedent(
            """
            [my job]

            num-to-dl = 3
            quiet = true

            users:
                therock: {self.tmpdir}
                squareenix: {self.tmpdir}
            """
        ).format(self=self)

        with open(os.path.join(self.tmpdir, 'batch.ini'), 'w') as batch_file:
            batch_file.write(cfg)

        self.assertEqual(
            main(["batch", os.path.join(self.tmpdir, 'batch.ini')]),
            0
        )

        self.assertEqual(
            len(glob.glob(os.path.join(self.tmpdir, '*.jpg'))), 6
        )
