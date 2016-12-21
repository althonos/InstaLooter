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




class TestInstaLooterProfileDownload(unittest.TestCase):

    MOST_POPULAR = [
        'instagram', 'selenagomez', 'taylorswift',
        'arianagrande', 'beyonce', 'kimkardashian',
        'cristiano', 'kyliejenner', 'therock',
    ]


    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    @classmethod
    def register_tests(cls):

        for profile in cls.MOST_POPULAR:
            cls._register_test(profile)

    @classmethod
    def _register_test(cls, profile):

        def _test(self):
            looter = instaLooter.InstaLooter(self.tmpdir, profile=profile, get_videos=True)
            looter.download(media_count=200)
            self.assertEqual(len(os.listdir(self.tmpdir)), min(200, int(looter.metadata['media']['count'])))
            self.assertEqual(profile, looter.metadata['username'])

        setattr(cls, "test_{}".format(profile), _test)

    def test_private_profile(self):
        looter = instaLooter.InstaLooter(self.tmpdir, profile="tldr")
        with self.assertRaises(StopIteration):
            next(looter.medias())

    def test_timeframe(self):
        looter = instaLooter.InstaLooter(self.tmpdir, profile="instagram")
        timeframe = (datetime.date(2016, 12, 17),)*2
        medias_in_timeframe = list(looter.medias(timeframe=timeframe))
        self.assertEqual(len(medias_in_timeframe), 3)


class TestInstaLooterHashtagDownload(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_hashtag_download(self):
        looter = instaLooter.InstaLooter(self.tmpdir, hashtag="python", get_videos=True)
        looter.download(media_count=200)
        self.assertEqual(len(os.listdir(self.tmpdir)), 200)





def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    TestInstaLooterProfileDownload.register_tests()
    suite.addTests(loader.loadTestsFromTestCase(TestInstaLooterProfileDownload))
    suite.addTests(loader.loadTestsFromTestCase(TestInstaLooterHashtagDownload))
    return suite


def setUpModule():
   warnings.simplefilter('ignore')

def tearDownModule():
   warnings.simplefilter(warnings.defaultaction)
