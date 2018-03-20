# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest
import datetime

import parameterized

from instalooter.cli._utils import time as timeutils

from .utils.method_names import firstparam


class TestTimeUtils(unittest.TestCase):

    @parameterized.parameterized.expand([
        (":", (None, None)),
        ("2017-03-12:", (datetime.date(2017, 3, 12), None)),
        (":2016-08-04", (None, datetime.date(2016, 8, 4))),
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
