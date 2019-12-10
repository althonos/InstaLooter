# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import unittest
import json
import os

import contexter
import fs
import parameterized
import requests
import six
from six.moves.queue import Queue

from instalooter.cli import main
from instalooter.cli import time as timeutils
from instalooter.cli import threadutils
from instalooter.cli.constants import USAGE
from instalooter.cli.login import login
from instalooter.worker import InstaDownloader

from .utils import mock
from .utils.method_names import firstparam
from .utils.ig_mock import MockPages


class TestCLI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    def setUp(self):
        self.destfs = fs.open_fs("temp://")
        self.tmpdir = self.destfs.getsyspath("/")

    def tearDown(self):
        self.destfs.close()

    def test_user(self):
        with contexter.Contexter() as ctx:
            ctx << mock.patch('instalooter.cli.ProfileLooter.pages', MockPages('nintendo'))
            r = main(["user", "nintendo", self.tmpdir, "-q", '-n', '10'])
        self.assertEqual(r, 0)
        self.assertEqual(len(self.destfs.listdir('/')), 10)

    def test_single_post(self):
        r = main(["post", "BFB6znLg5s1", self.tmpdir, "-q"])
        self.assertEqual(r, 0)
        self.assertTrue(self.destfs.exists("1243533605591030581.jpg"))

    def test_dump_json(self):
        r = main(["post", "BIqZ8L8AHmH", self.tmpdir, '-q', '-d'])
        self.assertEqual(r, 0)

        self.assertTrue(self.destfs.exists("1308972728853756295.json"))
        self.assertTrue(self.destfs.exists("1308972728853756295.jpg"))

        with self.destfs.open("1308972728853756295.json") as fp:
            json_metadata = json.load(fp)

        self.assertEqual("1308972728853756295", json_metadata["id"])
        self.assertEqual("BIqZ8L8AHmH", json_metadata["shortcode"])

    def test_dump_only(self):
        r = main(["post", "BIqZ8L8AHmH", self.tmpdir, '-q', '-D'])
        self.assertEqual(r, 0)

        self.assertTrue(self.destfs.exists("1308972728853756295.json"))
        self.assertFalse(self.destfs.exists("1308972728853756295.jpg"))

        with self.destfs.open("1308972728853756295.json") as fp:
            json_metadata = json.load(fp)

        self.assertEqual("1308972728853756295", json_metadata["id"])
        self.assertEqual("BIqZ8L8AHmH", json_metadata["shortcode"])

    def test_usage(self):
        handle = six.moves.StringIO()
        main(["--usage"], stream=handle)
        self.assertEqual(handle.getvalue().strip(), USAGE.strip())

    def test_single_post_from_url(self):
        url = "https://www.instagram.com/p/BFB6znLg5s1/"
        main(["post", url, self.tmpdir, "-q"])
        self.assertIn("1243533605591030581.jpg", os.listdir(self.tmpdir))


class TestTimeUtils(unittest.TestCase):

    @parameterized.parameterized.expand([
        (":", (None, None)),
        ("2017-03-12:", (None, datetime.date(2017, 3, 12))),
        (":2016-08-04", (datetime.date(2016, 8, 4), None)),
        ("2017-03-01:2017-02-01", (datetime.date(2017, 3, 1), datetime.date(2017, 2, 1))),
    ], testcase_func_name=firstparam)
    def test_get_times_from_cli(self, token, expected):
        self.assertEqual(timeutils.get_times_from_cli(token), expected)

    @parameterized.parameterized.expand([
        ("thisday", 0, 0),
        ("thisweek", 7, 7),
        ("thismonth", 28, 31),
        ("thisyear", 365, 366),
    ], testcase_func_name=firstparam)
    def test_get_times_from_cli_keywords(self, token, inf, sup):
        start, stop = timeutils.get_times_from_cli(token)
        self.assertGreaterEqual(start - stop, datetime.timedelta(inf))
        self.assertLessEqual(start - stop, datetime.timedelta(sup))
        self.assertEqual(start, datetime.date.today())

    @parameterized.parameterized.expand([
        ["x"],
        ["x:y"],
        ["x:y:z"],
    ], testcase_func_name=firstparam)
    def test_get_times_from_cli_bad_format(self, token):
        self.assertRaises(ValueError, timeutils.get_times_from_cli, token)


@mock.patch('instalooter.looters.InstaLooter._login')
@mock.patch('getpass.getpass')
class TestLoginUtils(unittest.TestCase):

    def test_cli_login_no_username(self, getpass_, login_):
        args = {'--username': None, "--password": None}
        login(args)
        login_.assert_not_called()

    @mock.patch('instalooter.looters.InstaLooter._logged_in')
    def test_cli_login_no_password(self, logged_in_, getpass_, login_):
        args = {'--username': "user", "--password": None, "--quiet": False}
        logged_in_.return_value = False
        getpass_.return_value = "pasw"
        login(args)
        login_.assert_called_once_with("user", "pasw")

    @mock.patch('instalooter.looters.InstaLooter._logged_in')
    def test_cli_login(self, logged_in_, getpass_, login_):
        args = {'--username': "user", "--password": "pasw", "--quiet": False}
        logged_in_.return_value = False
        login(args)
        login_.assert_called_once_with("user", "pasw")

    @mock.patch('instalooter.looters.InstaLooter._logged_in')
    def test_cli_already_logged_in(self, logged_in_, getpass_, login_):
        args = {'--username': "user", "--password": "pasw", "--quiet": False}
        logged_in_.return_value = True
        login(args)
        login_.assert_not_called()


class TestThreadUtils(unittest.TestCase):

    def test_threads_count(self):

        q = Queue()
        t1 = InstaDownloader(q, None, None)
        t2 = InstaDownloader(q, None, None)

        try:
            self.assertEqual(threadutils.threads_count(), 0)
            t1.start()
            self.assertEqual(threadutils.threads_count(), 1)
            t2.start()
            self.assertEqual(threadutils.threads_count(), 2)
        finally:
            t1.terminate()
            t2.terminate()

    def test_threads_force_join(self):

        q = Queue()
        t1 = InstaDownloader(q, None, None)
        t2 = InstaDownloader(q, None, None)

        t1.start()
        t2.start()

        self.assertTrue(t1.is_alive())
        self.assertTrue(t2.is_alive())

        threadutils.threads_force_join()

        self.assertFalse(t1.is_alive())
        self.assertFalse(t2.is_alive())
