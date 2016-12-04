import os
import shutil
import sys
import tempfile
import unittest
import warnings

sys.path.insert(0,
    os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
)

import instaLooter




class TestInstaLooterDownload(unittest.TestCase):

    MOST_POPULAR = [
        'instagram', 'selenagomez', 'taylorswift',
        'arianagrande', 'beyonce', 'kimkardashian',
        'cristiano', 'kyliejenner', 'justinbieber',
        'therock'
    ]

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    @classmethod
    def register_tests(cls):

        for profile in cls.MOST_POPULAR:

            def _test(self):
                looter = instaLooter.InstaLooter(self.tmpdir, profile=profile, get_videos=True)
                looter.download()
                self.assertEqual(len(os.listdir(self.tmpdir)), int(looter.metadata['media']['count']))
                self.assertEqual(profile, looter.metadata['username'])

            setattr(cls, "test_{}".format(profile), _test)


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
    TestInstaLooterDownload.register_tests()
    suite.addTests(loader.loadTestsFromTestCase(TestInstaLooterDownload))
    suite.addTests(loader.loadTestsFromTestCase(TestInstaLooterHashtagDownload))
    return suite


def setUpModule():
   warnings.simplefilter('ignore')

def tearDownModule():
   warnings.simplefilter(warnings.defaultaction)
