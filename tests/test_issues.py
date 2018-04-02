# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import os
import textwrap
import time
import unittest
import warnings

import fs
import requests
import six

from instalooter._impl import length_hint, piexif, PIL
from instalooter.batch import BatchRunner
from instalooter.cli import main
from instalooter.looters import HashtagLooter, ProfileLooter, PostLooter

from .utils import mock

# @mock.patch('instalooter.looter.requests.Session', lambda: TestResolvedIssues.session)
class TestResolvedIssues(unittest.TestCase):

    if six.PY2:
        assertRegex = unittest.TestCase.assertRegexpMatches

    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    def setUp(self):
        self.destfs = fs.open_fs("temp://")
        self.tmpdir = self.destfs.getsyspath("/")
        warnings._showwarning = warnings.showwarning

    def tearDown(self):
        self.destfs.close()
        warnings.showwarning = warnings._showwarning

    @unittest.expectedFailure
    @unittest.skipUnless(piexif, "piexif required for this test")
    def test_issue_009(self):
        """
        Thanks to @kurtmaia for reporting this bug.

        Checks that adding metadata to pictures downloaded from a hashtag
        works as well.
        """
        looter = ProfileLooter("fluoxetine", add_metadata=True, session=self.session)
        looter.download(self.destfs, media_count=10)

        for f in self.destfs.listdir("/"):
            exif = piexif.load(self.destfs.getbytes(f))
            self.assertTrue(exif['Exif']) # Date & Caption
            self.assertTrue(exif['0th'])  # Image creator

    def test_issue_012(self):
        """
        Feature request by @paramjitrohit.

        Allows downloading pictures and videos only within a timeframe.
        """
        looter = ProfileLooter("slotfaceofficial", session=self.session)
        day = datetime.date(2017, 2, 18)
        medias_in_timeframe = list(looter.medias(timeframe=[day, day]))
        self.assertEqual(len(medias_in_timeframe), 2)

    def test_issue_019(self):
        """
        Thanks to @emijawdo for reporting this bug.

        Checks that instalooter does not crash when not given a destination
        directory and uses the current directory.
        """
        initial_dir = os.getcwd()
        os.chdir(self.tmpdir)

        try:
            main(["user", "mysteryjets", "-n", "3", "-q"])
            self.assertEqual(len(self.destfs.listdir("/")), 3)
        finally:
            os.chdir(initial_dir)

    def test_issue_014(self):
        """
        Feature request by @JFLarsen.

        Allows customizing filenames using a template following Python
        `.format()` minilanguage.
        """

        looter = ProfileLooter(
            "mysteryjets", template="{username}.{id}", session=self.session)
        looter.download(self.destfs, media_count=5)

        for f in self.destfs.scandir("/"):
            self.assertTrue(f.name.startswith('mysteryjets'))

    @unittest.expectedFailure
    def test_issue_006(self):
        """
        Checks that instalooter does not iterate forever on a private
        profile.
        """
        looter = ProfileLooter("tldr", session=self.session)
        with self.assertRaises(StopIteration):
            next(looter.medias())

    def test_issue_015(self):
        """
        Feature request by @MohamedIM.

        Checks that videos are not downloaded several times if present
        already in the destination directory.
        """
        looter = ProfileLooter("instagram", session=self.session)
        looter.download_videos(self.destfs, media_count=1)

        video_file = next(self.destfs.filterdir("/", ["*.mp4"]))
        mtime = self.destfs.getdetails(video_file.name).accessed
        looter.download_videos(self.destfs, media_count=1)
        self.assertEqual(mtime, self.destfs.getdetails(video_file.name).accessed)

    def test_issue_022(self):
        """
        Thanks to @kuchenmitsahne for reporting this bug.

        Checks that using ``{datetime}`` in the template does not put
        a Windows forbidden character in the filename.
        """
        FORBIDDEN = set('<>:"/\|?*')

        looter = ProfileLooter(
            "mysteryjets", template="{datetime}", session=self.session)
        looter.download(self.destfs, media_count=5)
        for f in self.destfs.scandir("/"):
            self.assertFalse(FORBIDDEN.intersection(f.name))

    def test_issue_026(self):
        """
        Feature request by @verafide.

        Checks that pictures that are downloaded are not
        resized.
        """
        PostLooter("BO0XpEshejh", session=self.session).download(self.destfs)
        pic = PIL.Image.open(self.destfs.getsyspath("1419863760138791137.jpg"))
        self.assertEqual(pic.size, (525, 612))

    def test_issue_039(self):
        """
        Feature request by @verafide

        Checks that all pictures are downloaded from posts
        with more than one picture.
        """
        looter = PostLooter("BRHecUuFhPl", session=self.session)
        looter.download(self.destfs)
        self.assertEqual(
            set(self.destfs.listdir("/")),
            {
                "1461270165803344956.jpg",
                "1461270167497776767.jpg",
                "1461270174435133336.jpg",
                "1461270172581471925.jpg",
                "1461270181565655668.jpg",
            }
        )

    def test_issue_042(self):
        """
        Thanks to @MohamedIM for reporting this bug.

        Checks that a multipost is successfully downloaded from
        the CLI `post` option.
        """
        looter = PostLooter(
            'BRW-j_dBI6F', get_videos=True, session=self.session)
        looter.download(self.destfs)
        self.assertEqual(
            set(self.destfs.listdir("/")),
            {
                '1465633492745668095.mp4',
                '1465633517836005761.mp4',
                '1465633541559037966.mp4',
                '1465633561523918792.mp4',
            }
        )

    # OUTDATED: warn_windows is not used anymore
    #
    # def test_issue_044(self):
    #     """
    #     Thanks to @Bangaio64 for reporting this bug.
    #
    #     Checks that warn_windows does not trigger an exception.
    #     """
    #     import instalooter.utils
    #     warnings.showwarning = instalooter.utils.warn_windows
    #     looter = instalooter.InstaLooter(
    #         directory=self.tmpdir,
    #         profile="akjhdskjhfkjsdhfkjhdskjhfkjdshkfjhsdkjfdhkjdfshdfskhfd"
    #     )
    #     try:
    #         looter.download()
    #     except Exception:
    #         self.fail()

    def test_issue_041(self):
        """
        Feature request by @liorlior

        Allow downloading only videos.
        """
        looter = ProfileLooter("nintendo", videos_only=True, session=self.session)
        day = datetime.date(2017, 3, 10)
        looter.download(self.destfs, timeframe=[day, day])
        self.assertTrue(self.destfs.isfile("1467639884243493431.mp4"))

    def test_issue_052(self):
        """
        Thanks to @cyrusclarke for reporting this bug.

        Checks that on hashtags with a lot of posts, the time parameter
        doesn't cause the program to crash without finding any media to
        download.
        """
        main(["hashtag", "happy", self.tmpdir, "-q", "-t", "thisweek", "-n", "5"])
        self.assertGreaterEqual(len(self.destfs.listdir('/')), 5)

    # OUTDATED: Sidecar info dicts are not converted anymore but passed
    #           to the workers directly.
    #
    # def test_issue_057(self):
    #     """
    #     Thanks to @VasiliPupkin256 for reporting this bug.
    #
    #     Checks that metadata can successfully extract caption
    #     out of multiposts containing images.
    #     """
    #     looter = ProfileLooter("awwwwshoot_ob", session=self.session)
    #     sidecar = next(m for m in looter.medias() if m['__typename'] == "GraphSidecar")
    #
    #     looter = PostLooter(sidecar['shortcode'], session=self.session)
    #     looter.download(self.destfs)
    #
    #     for key in ('caption', 'code', 'date'):
    #         self.assertIn(key, media)
    #         self.assertIsNotNone(media[key])

    def test_issue_066(self):
        """
        Thanks to @douglasrizzo for reporting this bug.

        Check that likescount and commentscount can be used
        in filename templates without causing the program to
        crash.
        """
        looter = ProfileLooter(
            "zuck", get_videos=True, add_metadata=True,
            template='{id}-{likescount}-{commentscount}',
            session=self.session)
        looter.download(self.destfs, media_count=10)
        for image in self.destfs.listdir("/"):
            self.assertRegex(image, '[a-zA-Z0-9]*-[0-9]*-[0-9]*.(jpg|mp4)')

    def test_issue_076(self):
        """
        Thanks to @zeshuaro for reporting this bug.

        Check that when downloading hashtags, the downloader
        actually stops.
        """
        looter = HashtagLooter("oulianov", session=self.session)

        medias_it = looter.medias()
        postcount = length_hint(medias_it)

        for i, m in enumerate(medias_it):
            if i > postcount:
                self.fail("looter.medias() did not stop.")

    # OUTDATED: URLs are not modified anymore as Instagram prevents
    #           any modification
    #
    # def test_issue_082(self):
    #     """
    #     Thanks to @MohamedIM for reporting this bug.
    #
    #     Check that urls containing 'h-ak-igx' are not stripped from all
    #     their parameters.
    #     """
    #     looter = instalooter.looter.PostLooter('BWOYSYQDCo5', template='{code}')
    #     info = next(looter.medias())
    #
    #     info['display_url'] = \
    #         'https://ig-s-c-a.akamaihd.net/h-ak-igx/19764472_1586345694718446_4011887281420894208_n.jpg'
    #     looter.get_post_info = lambda code: info
    #
    #     looter.download_post('BWOYSYQDCo5')
    #
    #     with open(os.path.join(self.tmpdir, 'BWOYSYQDCo5.jpg'), 'rb') as f:
    #         self.assertNotIn(b'5xx Server Error', f.read())

    @unittest.expectedFailure
    def test_issue_084(self):
        """
        Thanks to @raphaelbernardino for reporting this bug.

        Make sure private profiles with few pictures (less than a page worth)
        raise the private warning as expected.
        """

        with warnings.catch_warnings(record=True) as registry:
            warnings.simplefilter('always')
            looter = ProfileLooter("raphaelbernardino", session=self.session)
            list(looter.medias())

        self.assertEqual(
            six.text_type(registry[0].message),
            u"Profile raphaelbernardino is private, retry after logging in."
        )

    @unittest.expectedFailure
    @unittest.skipUnless(piexif, "piexif required for this test")
    def test_issue_094(self):
        """
        Thanks to @jeanmarctst for raising this issue.

        Make sure caption is properly extracted from images downloaded
        from a post code and written to the metadata.
        """
        looter = PostLooter("BY77tSfBnRm",
            add_metadata=True, template='{code}', session=self.session)

        looter.download(self.destfs)
        metadata = piexif.load(self.destfs.getbytes("BY77tSfBnRm.jpg"), True)
        self.assertTrue(metadata['Exif']['UserComment'])

    def test_issue_125(self):
        """
        Thanks to @applepanda for reporting this bug.

        Make sure colons in path do not cause issue in batch mode.
        """
        configfile = six.StringIO(textwrap.dedent(
            """
            [Family]
            users =
            	instagram: D:\\Instagram\\Profiles\\instagram
            	therock: D:\\Instagram\\Profiles\\therock
            """
        ))
        runner = BatchRunner(configfile)
        self.assertEqual(
            runner.get_targets(runner._get('Family', 'users')),
            {'instagram': 'D:\\Instagram\\Profiles\\instagram',
             'therock': 'D:\\Instagram\\Profiles\\therock'}
        )


# @mock.patch('instalooter.looter.requests.Session', lambda: TestPullRequests.session)
class TestPullRequests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    def setUp(self):
        self.destfs = fs.open_fs("temp://")
        self.tmpdir = self.destfs.getsyspath("/")

    def tearDown(self):
        self.destfs.close()

    def test_pr_122(self):
        """
        Feature implemented by @susundberg.

        Set the access time and modification time of a downloaded media
        according to its IG date.
        """

        looter = ProfileLooter('franz_ferdinand',
            template='{code}', session=self.session)
        info = looter.get_post_info('BY77tSfBnRm')

        # Test download_post
        post_looter = PostLooter('BY77tSfBnRm',
            session=self.session, template='{code}')
        post_looter.download(self.destfs)
        stat = self.destfs.getdetails('BY77tSfBnRm.jpg')
        self.assertEqual(stat.raw["details"]["accessed"], info['taken_at_timestamp'])
        self.assertEqual(stat.raw["details"]["modified"], info['taken_at_timestamp'])

        # Test download_pictures
        pic = next(m for m in looter.medias() if not m['is_video'])
        looter.download_pictures(self.destfs, media_count=1)
        stat = self.destfs.getdetails('{}.jpg'.format(pic['shortcode']))
        self.assertEqual(stat.raw["details"]["accessed"], pic['taken_at_timestamp'])
        self.assertEqual(stat.raw["details"]["modified"], pic['taken_at_timestamp'])

        # Test download_videos
        vid = next(m for m in looter.medias() if m['is_video'])
        looter.download_videos(self.destfs, media_count=1)
        stat = self.destfs.getdetails('{}.mp4'.format(vid['shortcode']))
        self.assertEqual(stat.raw["details"]["accessed"], vid['taken_at_timestamp'])
        self.assertEqual(stat.raw["details"]["modified"], vid['taken_at_timestamp'])



def setUpModule():
   warnings.simplefilter('ignore')

def tearDownModule():
   warnings.simplefilter(warnings.defaultaction)
