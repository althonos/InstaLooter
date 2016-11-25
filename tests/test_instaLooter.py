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

        for username in cls.MOST_POPULAR:

            def _test(self):
                looter = instaLooter.InstaLooter(username, self.tmpdir, get_videos=True)
                looter.download()
                self.assertEqual(len(os.listdir(self.tmpdir)), int(looter.metadata['media']['count']))
                self.assertEqual(username, looter.metadata['username'])

            setattr(cls, "test_{}".format(username), _test)








def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    TestInstaLooterDownload.register_tests()
    suite.addTests(loader.loadTestsFromTestCase(TestInstaLooterDownload))
    return suite


def setUpModule():
   warnings.simplefilter('ignore')

def tearDownModule():
   warnings.simplefilter(warnings.defaultaction)
