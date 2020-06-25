# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import textwrap
import unittest
import warnings

import fs
import requests

from instalooter.cli import main
from instalooter.batch import BatchRunner
from instalooter.looters import InstaLooter


try:
    CONNECTION_FAILURE = not requests.get("https://instagr.am/instagram").ok
except requests.exceptions.ConnectionError:
    CONNECTION_FAILURE = True


class TestBatchRunner(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()
        InstaLooter._user_agent = cls.session.headers["User-Agent"]

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        del InstaLooter._user_agent

    def setUp(self):
        self.destfs = fs.open_fs("temp://")
        self.tmpdir = self.destfs.getsyspath("/")

    def tearDown(self):
        self.destfs.close()

    @unittest.skipIf(CONNECTION_FAILURE, "cannot connect to Instagram")
    def test_cli(self):
        cfg = textwrap.dedent(
            """
            [my job]

            num-to-dl = 3
            quiet = true

            users:
                therock: {self.tmpdir}
                nintendo: {self.tmpdir}
            """
        ).format(self=self)

        with self.destfs.open('batch.ini', 'w') as batch_file:
            batch_file.write(cfg)

        retcode = main(["batch", self.destfs.getsyspath('batch.ini')])
        self.assertEqual(retcode, 0)
        self.assertGreaterEqual(
            len(list(self.destfs.filterdir("/", ["*.jpg"]))), 6)


def setUpModule():
   warnings.simplefilter('ignore')


def tearDownModule():
   warnings.simplefilter(warnings.defaultaction)
