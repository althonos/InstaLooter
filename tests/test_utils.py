import unittest
import datetime

from instaLooter import utils


class TestUtils(unittest.TestCase):

    def test_get_times_from_cli_wrong_format(self):

        with self.assertRaises(ValueError):
            utils.get_times_from_cli("xxx")

        with self.assertRaises(ValueError):
            utils.get_times_from_cli("xxx:yyy:zzz")

        with self.assertRaises(ValueError):
            utils.get_times_from_cli("xxx:yyy")

    def test_get_times_from_cli_keywords(self):

        for token, delta in [("thisday", 0), ("thisweek", 7)]:
            start, stop = utils.get_times_from_cli(token)
            self.assertEqual(start - stop, datetime.timedelta(delta))

        for token, small, large in [("thismonth", 28, 31), ("thisyear", 365, 366)]:
            start, stop = utils.get_times_from_cli(token)
            self.assertGreaterEqual(start - stop, datetime.timedelta(small))
            self.assertLessEqual(start - stop, datetime.timedelta(large))

    def test_get_times_from_cli(self):

        results = {
            ":": None,
            "2017-03-12:": (datetime.date(2017, 3, 12), None),
            ":2016-08-04": (None, datetime.date(2016, 8, 4)),
            "2017-03-01:2017-02-01": (datetime.date(2017, 3, 1), datetime.date(2017, 2, 1)),
        }

        for token, expected in results.items():
            self.assertEqual(utils.get_times_from_cli(token), expected)
