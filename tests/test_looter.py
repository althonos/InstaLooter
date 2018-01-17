# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import re
import sys
import glob
import json
import shutil
import requests
import tempfile
import unittest
import warnings
import operator
import itertools

import instaLooter



class _TempTestCase(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


class TestProfileDownload(_TempTestCase):

    MOST_POPULAR = [
        'instagram', 'selenagomez', 'taylorswift',
        'arianagrande', 'beyonce', 'kimkardashian',
        'cristiano', 'kyliejenner', 'therock',
    ]

    MEDIA_COUNT = 30

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


class TestHashtagDownload(_TempTestCase):

    MEDIA_COUNT = 30

    def test_hashtag_download(self):
        looter = instaLooter.InstaLooter(self.tmpdir, hashtag="python", get_videos=True)
        looter.download(media_count=self.MEDIA_COUNT)
        self.assertEqual(len(os.listdir(self.tmpdir)), self.MEDIA_COUNT)


class TestTemplate(_TempTestCase):

    MEDIA_COUNT = 30

    def test_template_1(self):
        profile = "therock"
        looter = instaLooter.InstaLooter(
            self.tmpdir, profile=profile, get_videos=True,
            template='{username}-{id}'
        )
        looter.download(media_count=self.MEDIA_COUNT, with_pbar=False)
        for f in os.listdir(self.tmpdir):
            self.assertTrue(f.startswith(profile))


class TestDump(_TempTestCase):

    def assertMediaEqual(self, media, dump):
        for key in ['__typename', 'date', 'dimensions', 'display_src',
                    'is_video', 'media_preview']:
            self.assertEqual(media[key], dump[key])

        self.assertEqual(
            media.get('code') or media['shortcode'],
            dump.get('code' or dump['shortcode'])
        )
        self.assertEqual(
            media['owner']['id'],
            dump['owner']['id']
        )
        self.assertIn('likes', dump)
        self.assertIn('comments', dump)

    def test_dump_json(self):
        looter = instaLooter.InstaLooter(
            self.tmpdir,
            profile="instagram",
            dump_json=True,
        )
        test_medias = list(itertools.islice(
            (m for m in looter.medias() if not m['is_video']), 3))
        looter.download(media_count=3)

        # Check all files were downloaded as expected
        self.assertEqual(
            sorted(os.listdir(self.tmpdir)),
            sorted(f for media in test_medias for f in (
                str("{}.jpg").format(media['id']),
                str("{}.json").format(media['id']),
            ))
        )

        # Check the metadata are OK
        for media in test_medias:
            with open(os.path.join(self.tmpdir, "{}.json").format(media['id'])) as f:
                dump = json.load(f)
            self.assertMediaEqual(media, dump)

    def test_dump_only(self):
        looter = instaLooter.InstaLooter(
            self.tmpdir,
            profile="instagram",
            dump_only=True,
        )
        test_medias = list(itertools.islice(
            (m for m in looter.medias() if not m['is_video']), 3))
        looter.download(media_count=3)

        # Check all files were downloaded as expected
        self.assertEqual(
            sorted(os.listdir(self.tmpdir)),
            sorted(str("{}.json").format(media['id']) for media in test_medias)
        )

        # Check the metadata are OK
        for media in test_medias:
            with open(os.path.join(self.tmpdir, "{}.json").format(media['id'])) as f:
                dump = json.load(f)
            self.assertMediaEqual(media, dump)

    def test_extended_dump(self):
        looter = instaLooter.InstaLooter(
            self.tmpdir,
            profile="instagram",
            dump_only=True,
            extended_dump=True,
        )
        test_medias = list(itertools.islice(
            (m for m in looter.medias() if not m['is_video']), 3))
        looter.download(media_count=3)

        # Check all files were downloaded as expected
        self.assertEqual(
            sorted(os.listdir(self.tmpdir)),
            sorted(str("{}.json").format(media['id']) for media in test_medias)
        )

        # Check the metadata are OK
        for media in test_medias:
            with open(os.path.join(self.tmpdir, "{}.json").format(media['id'])) as f:
                dump = json.load(f)
            self.assertMediaEqual(media, dump)

            # Check the dump was "extended"
            self.assertIn('edge_media_to_comment', dump)
            self.assertIn('edge_media_to_caption', dump)


class TestUtils(_TempTestCase):

    MEDIA_COUNT = 30

    def setUp(self):
        super(TestUtils, self).setUp()
        self.looter = instaLooter.InstaLooter()

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

    @unittest.skipIf(sys.version_info < (3,4),
                     "operator.length_hint is a 3.4+ feature.")
    def test_length_hint_empty(self):

        looter = instaLooter.InstaLooter(profile="jkshksjdhfjkhdkfhk")
        self.assertEqual(operator.length_hint(looter), 0)

        looter = instaLooter.InstaLooter(hashtag="jkshksjdhfjkhdkfhk")
        self.assertEqual(operator.length_hint(looter), 0)

    @unittest.skipIf(sys.version_info < (3,4),
                     "operator.length_hint is a 3.4+ feature.")
    def test_length_hint(self):

        looter = instaLooter.InstaLooter(self.tmpdir, profile="tide")
        hint = operator.length_hint(looter)

        # Check the post count is greater than 0
        self.assertGreater(hint, 0)

        # Download pictures and check if the count
        # match (at most as many posts downloaded)
        looter.download()
        self.assertLessEqual(len(os.listdir(self.tmpdir)), hint)
        
        
class TestTorManager(_TempTestCase):

    def test_proxy_setup(self):
        looter = instaLooter.InstaLooter(socks_port=9090)
        self.assertTrue(hasattr(looter, 'tor_manager'))
        self.assertTrue(str(looter.session.proxies) == str(looter.tor_manager.proxies))
        self.assertTrue(isinstance(looter.session.hooks.get('response', None), type(looter.tor_manager.call_for_new_ip)))
        
    def test_ip_changeability(self):
        def get_ip(proxies):
            r = requests.get('https://api.ipify.org?format=json', proxies=proxies)
            return json.loads(r.text)['ip']
            
        looter = instaLooter.InstaLooter(socks_port=9090, change_ip_after=1)
        old_ip = get_ip(looter.tor_manager.proxies)
        
        looter.session.get('https://www.instagram.com/')
        new_ip = get_ip(looter.tor_manager.proxies)
        
        self.assertTrue(old_ip != new_ip)


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    TestProfileDownload.register_tests()
    suite.addTests(loader.loadTestsFromTestCase(TestProfileDownload))
    suite.addTests(loader.loadTestsFromTestCase(TestHashtagDownload))
    suite.addTests(loader.loadTestsFromTestCase(TestTemplate))
    suite.addTests(loader.loadTestsFromTestCase(TestTorManager))
    return suite


def setUpModule():
   warnings.simplefilter('ignore')


def tearDownModule():
   warnings.simplefilter(warnings.defaultaction)
