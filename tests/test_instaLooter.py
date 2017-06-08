import os
import re
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

            # We have to use GreaterEqual since multi media posts
            # are counted as 1 but will download more than one
            # picture / video
            self.assertGreaterEqual(len(os.listdir(self.tmpdir)), min(200, int(looter.metadata['media']['count'])))
            self.assertEqual(profile, looter.metadata['username'])

        setattr(cls, "test_{}".format(profile), _test)


class TestInstaLooterHashtagDownload(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_hashtag_download(self):
        looter = instaLooter.InstaLooter(self.tmpdir, hashtag="python", get_videos=True)
        looter.download(media_count=50)
        self.assertEqual(len(os.listdir(self.tmpdir)), 50)


class TestInstaLooterTemplate(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_template_1(self):
        PROFILE = "therock"
        looter = instaLooter.InstaLooter(
            self.tmpdir, profile=PROFILE, get_videos=True,
            template='{username}-{id}'
        )
        looter.download(media_count=30, with_pbar=False)
        for f in os.listdir(self.tmpdir):
            self.assertTrue(f.startswith(PROFILE))


class TestInstaLooterUtils(unittest.TestCase):

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

    def test_url_generator_resize(self):

        def square_resizer(media):
            cleaning_regex = re.compile(r"(s[0-9x]*/)?(e[0-9]*)/")
            return cleaning_regex.sub('s320x320/', media['display_src'])

        self.looter = instaLooter.InstaLooter(
            self.tmpdir, url_generator=square_resizer
        )

        self.looter.download_post("BFB6znLg5s1")

        with PIL.Image.open(os.path.join(self.tmpdir, '1243533605591030581.jpg')) as img:
            width, height = img.size
            self.assertEqual(width, 320)
            self.assertEqual(height, 320)




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
