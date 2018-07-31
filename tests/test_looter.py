# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest
import warnings

import fs.memoryfs
import parameterized
import requests
import six

from instalooter.looters import ProfileLooter, HashtagLooter, PostLooter

from .utils import mock
from .utils.method_names import signature


class TestInstaLooter(unittest.TestCase):

    MEDIA_COUNT = 5

    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    def setUp(self):
        self.destfs = fs.memoryfs.MemoryFS()

    def tearDown(self):
        self.destfs.close()

    @parameterized.parameterized.expand([
        parameterized.param("instagram",),
        parameterized.param("instagram", get_videos=True),
        # parameterized.param("serotonine",),
    ], testcase_func_name=signature)
    def test_profile(self, profile, **kwargs):
        looter = ProfileLooter(profile, session=self.session, **kwargs)
        looter.download(self.destfs, media_count=self.MEDIA_COUNT)
        self.assertGreaterEqual(len(self.destfs.listdir("/")), self.MEDIA_COUNT)

    @parameterized.parameterized.expand([
        parameterized.param("eggs"),
        parameterized.param("python", videos_only=True),
    ], testcase_func_name=signature)
    def test_hashtag(self, hashtag, **kwargs):
        looter = HashtagLooter(hashtag, session=self.session, **kwargs)
        looter.download(self.destfs, media_count=self.MEDIA_COUNT)
        self.assertGreaterEqual(len(self.destfs.listdir("/")), self.MEDIA_COUNT)



class TestPostLooter(unittest.TestCase):

    @mock.patch('instalooter.looters.InstaLooter.__init__')
    def test_post_url(self, _):
        urls = (
            "http://www.instagram.com/p/BJlIB9WhdRn/?taken-by=2k",
            "https://www.instagram.com/p/BJlIB9WhdRn/?taken-by=2k",
            "www.instagram.com/p/BJlIB9WhdRn/?taken-by=2k",
            "http://instagr.am/p/BJlIB9WhdRn/?taken-by=2k",
            "https://instagr.am/p/BJlIB9WhdRn/?taken-by=2k",
            "instagr.am/p/BJlIB9WhdRn/?taken-by=2k",
        )
        for url in urls:
            looter = PostLooter(url)
            self.assertEqual(looter.code, "BJlIB9WhdRn")

    @mock.patch('instalooter.looters.InstaLooter.__init__')
    def test_invalid_post_code(self, _):
        with self.assertRaises(ValueError):
            looter = PostLooter("instagram")  # invalid code


# class TestTemplate(_TempTestCase):
#
#     MEDIA_COUNT = 30
#
#     def test_template_1(self):
#         profile = "therock"
#         looter = instaLooter.InstaLooter(
#             self.tmpdir, profile=profile, get_videos=True,
#             template='{username}-{id}'
#         )
#         looter.download(media_count=self.MEDIA_COUNT, with_pbar=False)
#         for f in os.listdir(self.tmpdir):
#             self.assertTrue(f.startswith(profile))
#
#
# class TestDump(_TempTestCase):
#
#     def assertMediaEqual(self, media, dump):
#         for key in ['__typename', 'date', 'dimensions', 'display_src',
#                     'is_video', 'media_preview']:
#             self.assertEqual(media[key], dump[key])
#
#         self.assertEqual(
#             media.get('code') or media['shortcode'],
#             dump.get('code' or dump['shortcode'])
#         )
#         self.assertEqual(
#             media['owner']['id'],
#             dump['owner']['id']
#         )
#         self.assertIn('likes', dump)
#         self.assertIn('comments', dump)
#
#     def test_dump_json(self):
#         looter = instaLooter.InstaLooter(
#             self.tmpdir,
#             profile="instagram",
#             dump_json=True,
#         )
#         test_medias = list(itertools.islice(
#             (m for m in looter.medias() if not m['is_video']), 3))
#         looter.download(media_count=3)
#
#         # Check all files were downloaded as expected
#         self.assertEqual(
#             sorted(os.listdir(self.tmpdir)),
#             sorted(f for media in test_medias for f in (
#                 str("{}.jpg").format(media['id']),
#                 str("{}.json").format(media['id']),
#             ))
#         )
#
#         # Check the metadata are OK
#         for media in test_medias:
#             with open(os.path.join(self.tmpdir, "{}.json").format(media['id'])) as f:
#                 dump = json.load(f)
#             self.assertMediaEqual(media, dump)
#
#     def test_dump_only(self):
#         looter = instaLooter.InstaLooter(
#             self.tmpdir,
#             profile="instagram",
#             dump_only=True,
#         )
#         test_medias = list(itertools.islice(
#             (m for m in looter.medias() if not m['is_video']), 3))
#         looter.download(media_count=3)
#
#         # Check all files were downloaded as expected
#         self.assertEqual(
#             sorted(os.listdir(self.tmpdir)),
#             sorted(str("{}.json").format(media['id']) for media in test_medias)
#         )
#
#         # Check the metadata are OK
#         for media in test_medias:
#             with open(os.path.join(self.tmpdir, "{}.json").format(media['id'])) as f:
#                 dump = json.load(f)
#             self.assertMediaEqual(media, dump)
#
#     def test_extended_dump(self):
#         looter = instaLooter.InstaLooter(
#             self.tmpdir,
#             profile="instagram",
#             dump_only=True,
#             extended_dump=True,
#         )
#         test_medias = list(itertools.islice(
#             (m for m in looter.medias() if not m['is_video']), 3))
#         looter.download(media_count=3)
#
#         # Check all files were downloaded as expected
#         self.assertEqual(
#             sorted(os.listdir(self.tmpdir)),
#             sorted(str("{}.json").format(media['id']) for media in test_medias)
#         )
#
#         # Check the metadata are OK
#         for media in test_medias:
#             with open(os.path.join(self.tmpdir, "{}.json").format(media['id'])) as f:
#                 dump = json.load(f)
#             self.assertMediaEqual(media, dump)
#
#             # Check the dump was "extended"
#             self.assertIn('edge_media_to_comment', dump)
#             self.assertIn('edge_media_to_caption', dump)
#
#
# class TestUtils(_TempTestCase):
#
#     MEDIA_COUNT = 30
#
#     def setUp(self):
#         super(TestUtils, self).setUp()
#         self.looter = instaLooter.InstaLooter()
#
#     def test_extract_post_code_from_url(self):
#         url = "https://www.instagram.com/p/BFB6znLg5s1/"
#
#         self.assertEqual(
#             self.looter._extract_code_from_url(url),
#             'BFB6znLg5s1',
#         )
#
#         with self.assertRaises(ValueError):
#             self.looter._extract_code_from_url(
#                 'https://www.instagram.com/'
#             )
#
#     def test_get_owner_info(self):
#         therock = self.looter.get_owner_info("BTHqEhWFR4y")
#         self.assertEqual(therock['username'], 'therock')
#         self.assertEqual(therock['id'], '232192182')
#         self.assertFalse(therock['is_private'])
#
#         gearbox = self.looter.get_owner_info("BfMWE3aFsEh")
#         self.assertEqual(gearbox['username'], 'gearboxsoftware')
#         self.assertEqual(gearbox['id'], '1409542965')
#         self.assertFalse(gearbox['is_private'])
#
#     def test_url_generator_nocallable(self):
#         with self.assertRaises(ValueError):
#             self.looter = instaLooter.InstaLooter(
#                 self.tmpdir, profile="instagram", url_generator=1
#             )
#
#     @unittest.skipIf(sys.version_info < (3,4),
#                      "operator.length_hint is a 3.4+ feature.")
#     def test_length_hint_empty(self):
#
#         looter = instaLooter.InstaLooter(profile="jkshksjdhfjkhdkfhk")
#         self.assertEqual(operator.length_hint(looter), 0)
#
#         looter = instaLooter.InstaLooter(hashtag="jkshksjdhfjkhdkfhk")
#         self.assertEqual(operator.length_hint(looter), 0)
#
#     @unittest.skipIf(sys.version_info < (3,4),
#                      "operator.length_hint is a 3.4+ feature.")
#     def test_length_hint(self):
#
#         looter = instaLooter.InstaLooter(self.tmpdir, profile="tide")
#         hint = operator.length_hint(looter)
#
#         # Check the post count is greater than 0
#         self.assertGreater(hint, 0)
#
#         # Download pictures and check if the count
#         # match (at most as many posts downloaded)
#         looter.download()
#         self.assertLessEqual(len(os.listdir(self.tmpdir)), hint)


# def load_tests(loader, tests, pattern):
#     suite = unittest.TestSuite()
#     TestProfileLooter.register_tests()
#     suite.addTests(loader.loadTestsFromTestCase(TestProfileLooter))
#     # suite.addTests(loader.loadTestsFromTestCase(TestHashtagDownload))
#     # suite.addTests(loader.loadTestsFromTestCase(TestTemplate))
#     return suite


def setUpModule():
   warnings.simplefilter('ignore')


def tearDownModule():
   warnings.simplefilter(warnings.defaultaction)
