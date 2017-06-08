import os
import re
import glob
import shutil
import tempfile
import unittest
import warnings
import PIL.Image

import instaLooter




class TestInstaLooterProfileDownload(unittest.TestCase):

    MOST_POPULAR = [
        'instagram', 'selenagomez', 'taylorswift',
        'arianagrande', 'beyonce', 'kimkardashian',
        'cristiano', 'kyliejenner', 'therock',
    ]

    MEDIA_COUNT = 30

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
            looter.download(media_count=cls.MEDIA_COUNT)

            # We have to use GreaterEqual since multi media posts
            # are counted as 1 but will download more than one
            # picture / video
            self.assertGreaterEqual(
                len(os.listdir(self.tmpdir)),
                min(cls.MEDIA_COUNT, int(looter.metadata['media']['count']))
            )
            self.assertEqual(profile, looter.metadata['username'])

        setattr(cls, "test_{}".format(profile), _test)


class TestInstaLooterHashtagDownload(unittest.TestCase):

    MEDIA_COUNT = 30

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_hashtag_download(self):
        looter = instaLooter.InstaLooter(self.tmpdir, hashtag="python", get_videos=True)
        looter.download(media_count=self.MEDIA_COUNT)
        self.assertEqual(len(os.listdir(self.tmpdir)), self.MEDIA_COUNT)


class TestInstaLooterTemplate(unittest.TestCase):

    MEDIA_COUNT = 30

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_template_1(self):
        profile = "therock"
        looter = instaLooter.InstaLooter(
            self.tmpdir, profile=profile, get_videos=True,
            template='{username}-{id}'
        )
        looter.download(media_count=self.MEDIA_COUNT, with_pbar=False)
        for f in os.listdir(self.tmpdir):
            self.assertTrue(f.startswith(profile))


class TestInstaLooterUtils(unittest.TestCase):

    MEDIA_COUNT = 30

    def setUp(self):
        self.looter = instaLooter.InstaLooter()
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_extract_post_code_from_url(self):
        url = "https://www.instagram.com/p/BFB6znLg5s1/"

        self.assertEqual(
            self.looter._extract_code_from_url(url),
            'BFB6znLg5s1',
        )

        with self.assertRaises(ValueError):
            self.looter._extract_code_from_url(
                'https://www.instagram.com/'
            )

    def test_get_owner_info(self):
        therock = self.looter.get_owner_info("BTHqEhWFR4y")
        self.assertEqual(therock['username'], 'therock')
        self.assertEqual(therock['id'], '232192182')
        self.assertFalse(therock['is_private'])

        squareenix = self.looter.get_owner_info("BS9UVpcjfCZ")
        self.assertEqual(squareenix['username'], 'squareenix')
        self.assertEqual(squareenix['id'], '2117884847')
        self.assertFalse(squareenix['is_private'])

    def test_url_generator_nocallable(self):
        with self.assertRaises(ValueError):
            self.looter = instaLooter.InstaLooter(
                self.tmpdir, profile="instagram", url_generator=1
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
