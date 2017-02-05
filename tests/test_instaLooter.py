import os
import shutil
import sys
import tempfile
import unittest
import warnings
import datetime

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


class TestInstaLooterHashtagDownload(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_hashtag_download(self):
        looter = instaLooter.InstaLooter(self.tmpdir, hashtag="python", get_videos=True)
        looter.download(media_count=200)
        self.assertEqual(len(os.listdir(self.tmpdir)), 200)


class TestInstaLooterTemplate(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_template_1(self):
        PROFILE = "therock"
        looter = instaLooter.InstaLooter(self.tmpdir, profile=PROFILE, get_videos=True, template='{username}')
        looter.download(media_count=30, with_pbar=True)
        for f in os.listdir(self.tmpdir):
            self.assertTrue(f.startswith(PROFILE))


class TestInstaLooterUtils(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_extract_post_code_from_url(self):
        url = "https://www.instagram.com/p/BFB6znLg5s1/"

        self.assertEqual(
            instaLooter.InstaLooter._extract_code_from_url(url),
            'BFB6znLg5s1',
        )

        with self.assertRaises(ValueError):
            instaLooter.InstaLooter._extract_code_from_url(
                'https://www.instagram.com/'
            )



def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    TestInstaLooterProfileDownload.register_tests()
    suite.addTests(loader.loadTestsFromTestCase(TestInstaLooterProfileDownload))
    suite.addTests(loader.loadTestsFromTestCase(TestInstaLooterHashtagDownload))
    suite.addTests(loader.loadTestsFromTestCase(TestInstaLooterTemplate))
    return suite

def setUpModule():
   warnings.simplefilter('ignore')

def tearDownModule():
   warnings.simplefilter(warnings.defaultaction)
