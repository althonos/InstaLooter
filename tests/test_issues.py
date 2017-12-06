# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import six
import operator
import unittest
import tempfile
import shutil
import glob
import datetime
import warnings
import piexif
import PIL.Image

import instaLooter



class TestResolvedIssues(unittest.TestCase):

    if six.PY2:
        assertRegex = unittest.TestCase.assertRegexpMatches

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        warnings._showwarning = warnings.showwarning

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        warnings.showwarning = warnings._showwarning

    def test_issue_09(self):
        """
        Thanks to @kurtmaia for reporting this bug.

        Checks that adding metadata to pictures downloaded from a hashtag
        works as well.
        """
        instaLooter.main(["fluoxetine", self.tmpdir, "-n", "10", "-q", "-m"])
        for f in os.listdir(self.tmpdir):
            exif = piexif.load(os.path.join(self.tmpdir, f))
            self.assertTrue(exif['Exif']) # Date & Caption
            self.assertTrue(exif['0th'])  # Image creator

    def test_issue_12(self):
        """
        Feature request by @paramjitrohit.

        Allows downloading pictures and videos only within a timeframe.
        """
        looter = instaLooter.InstaLooter(self.tmpdir, profile="slotfaceofficial")
        timeframe = (datetime.date(2017, 2, 18),)*2
        medias_in_timeframe = list(looter.medias(timeframe=timeframe))
        self.assertEqual(len(medias_in_timeframe), 2)

    def test_issue_19(self):
        """
        Thanks to @emijawdo for reporting this bug.

        Checks that instaLooter does not crash when not given a destination
        directory and uses the current directory.
        """
        initial_dir = os.getcwd()
        os.chdir(self.tmpdir)
        instaLooter.main(["mysteryjets", "-n", "10", "-q"])
        self.assertEqual(len(os.listdir(self.tmpdir)), 10)
        os.chdir(initial_dir)

    def test_issue_14(self):
        """
        Feature request by @JFLarsen.

        Allows customizing filenames using a template following Python
        `.format()` minilanguage.
        """
        instaLooter.main(["mysteryjets", self.tmpdir, "-n", "10", "-q", "-T", "{username}.{date}.{id}"])
        for f in os.listdir(self.tmpdir):
            self.assertTrue(f.startswith('mysteryjets'))

    def test_issue_06(self):
        """
        Checks that instaLooter does not iterate forever on a private
        profile.
        """
        looter = instaLooter.InstaLooter(self.tmpdir, profile="tldr")
        with self.assertRaises(StopIteration):
            next(looter.medias())

    def test_issue_15(self):
        """
        Feature request by @MohamedIM.

        Checks that videos are not downloaded several times if present
        already in the destination directory.
        """
        looter = instaLooter.InstaLooter(self.tmpdir, profile="instagram")
        looter.download_videos(media_count=1)
        video_file = next(glob.iglob(os.path.join(self.tmpdir, '*.mp4')))
        mtime = os.stat(video_file).st_mtime
        looter.download_videos(media_count=1)#, new_only=True)
        self.assertEqual(mtime, os.stat(video_file).st_mtime)

    def test_issue_22(self):
        """
        Thanks to @kuchenmitsahne for reporting this bug.

        Checks that using ``{datetime}`` in the template does not put
        a Windows forbidden character in the filename.
        """
        FORBIDDEN = '<>:"/\|?*'
        instaLooter.main(["mysteryjets", self.tmpdir, "-n", "10", "-q", "-T", "{datetime}"])
        for f in os.listdir(self.tmpdir):
            for char in FORBIDDEN:
                self.assertNotIn(char, f)

    def test_issue_26(self):
        """
        Feature request by @verafide.

        Checks that pictures that are downloaded are not
        resized.
        """
        looter = instaLooter.InstaLooter(self.tmpdir)
        looter.download_post("BO0XpEshejh")
        filename = "1419863760138791137.jpg"
        pic = PIL.Image.open(os.path.join(self.tmpdir, filename))
        self.assertEqual(pic.size, (525, 612))

    def test_issue_39(self):
        """
        Feature request by @verafide

        Checks that all pictures are downloaded from posts
        with more than one picture.
        """
        looter = instaLooter.InstaLooter(self.tmpdir)
        looter.download_post("BRHecUuFhPl")
        self.assertEqual(
            set(os.listdir(self.tmpdir)),
            {
                "1461270165803344956.jpg",
                "1461270167497776767.jpg",
                "1461270174435133336.jpg",
                "1461270172581471925.jpg",
                "1461270181565655668.jpg",
            }
        )

    def test_issue_42(self):
        """
        Thanks to @MohamedIM for reporting this bug.

        Checks that a multipost is successfully downloaded from
        the CLI `post` option.
        """
        looter = instaLooter.InstaLooter(self.tmpdir)
        looter.download_post('BRW-j_dBI6F')
        self.assertEqual(
            set(os.listdir(self.tmpdir)),
            {
                '1465633492745668095.mp4',
                '1465633517836005761.mp4',
                '1465633541559037966.mp4',
                '1465633561523918792.mp4',
            }
        )

    def test_issue_44(self):
        """
        Thanks to @Bangaio64 for reporting this bug.

        Checks that warn_windows does not trigger an exception.
        """
        import instaLooter.utils
        warnings.showwarning = instaLooter.utils.warn_windows
        looter = instaLooter.InstaLooter(
            directory=self.tmpdir,
            profile="akjhdskjhfkjsdhfkjhdskjhfkjdshkfjhsdkjfdhkjdfshdfskhfd"
        )
        try:
            looter.download()
        except Exception:
            self.fail()

    def test_issue_41(self):
        """
        Feature request by @liorlior

        Allow downloading only videos.
        """
        looter = instaLooter.InstaLooter(self.tmpdir, profile="nintendo", videos_only=True)
        looter.download(timeframe=(datetime.date(2017, 3, 10), )*2)
        self.assertEqual(os.listdir(self.tmpdir), ["1467639884243493431.mp4"])

    def test_issue_52(self):
        """
        Thanks to @cyrusclarke for reporting this bug.

        Checks that on hashtags with a lot of posts, the time parameter
        doesn't cause the program to crash without finding any media to
        download.
        """
        instaLooter.main(["hashtag", "happy", self.tmpdir, "-q", "-t", "thisweek", "-n", "20"])
        self.assertEqual(len(os.listdir(self.tmpdir)), 20)

    def test_issue_57(self):
        """
        Thanks to @VasiliPupkin256 for reporting this bug.

        Checks that metadata can successfully extract caption
        out of multiposts containing images.
        """
        looter = instaLooter.InstaLooter(
            self.tmpdir, profile="awwwwshoot_ob", get_videos=True,
            add_metadata=True
        )

        looter._medias_queue = six.moves.queue.Queue()
        looter._fill_media_queue()

        while not looter._medias_queue.empty():
            media = looter._medias_queue.get()
            for key in ('caption', 'code', 'date'):
                self.assertIn(key, media)
                self.assertIsNotNone(media[key])

    def test_issue_66(self):
        """
        Thanks to @douglasrizzo for reporting this bug.

        Check that likescount and commentscount can be used
        in filename templates without causing the program to
        crash.
        """
        looter = instaLooter.InstaLooter(
            self.tmpdir, profile="zuck",
            get_videos=True, add_metadata=True,
            template='{id}-{likescount}-{commentscount}',
        )
        looter.download(media_count=10)
        for image in os.listdir(self.tmpdir):
            self.assertRegex(image, '[a-zA-Z0-9]*-[0-9]*-[0-9]*.(jpg|mp4)')

    def test_issue_76(self):
        """
        Thanks to @zeshuaro for reporting this bug.

        Check that when downloading hashtags, the downloader
        actually stops.
        """
        looter = instaLooter.InstaLooter(self.tmpdir, hashtag="oulianov")
        postcount = looter.__length_hint__() # operator.length_hint

        for i, m in enumerate(looter.medias()):
            if i > postcount:
                self.fail("looter.medias() did not stop.")

    def test_issue_82(self):
        """
        Thanks to @MohamedIM for reporting this bug.

        Check that urls containing 'h-ak-igx' are not stripped from all
        their parameters.
        """
        looter = instaLooter.InstaLooter(self.tmpdir, template='{code}')
        info = looter.get_post_info('BWOYSYQDCo5')

        info['display_url'] = \
            'https://ig-s-c-a.akamaihd.net/h-ak-igx/19764472_1586345694718446_4011887281420894208_n.jpg'
        looter.get_post_info = lambda code: info

        looter.download_post('BWOYSYQDCo5')

        with open(os.path.join(self.tmpdir, 'BWOYSYQDCo5.jpg'), 'rb') as f:
            self.assertNotIn(b'5xx Server Error', f.read())

    def test_issue_84(self):
        """
        Thanks to @raphaelbernardino for reporting this bug.

        Make sure private profiles with few pictures (less than a page worth)
        raise the private warning as expected.
        """

        with warnings.catch_warnings(record=True) as registry:
            warnings.simplefilter('always')
            looter = instaLooter.InstaLooter(profile="raphaelbernardino")
            list(looter.medias())

        self.assertEqual(
            six.text_type(registry[0].message),
            u"Profile raphaelbernardino is private, retry after logging in."
        )

    def test_issue_94(self):
        """
        Thanks to @jeanmarctst for raising this issue.

        Make sure caption is properly extracted from images downloaded
        from a post code and written to the metadata.
        """
        looter = instaLooter.InstaLooter(
            self.tmpdir, add_metadata=True, template='{code}')
        looter.download_post('BY77tSfBnRm')
        metadata = piexif.load(
            os.path.join(self.tmpdir, 'BY77tSfBnRm.jpg'), True)
        self.assertTrue(metadata['Exif']['UserComment'])



class TestPullRequests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        warnings._showwarning = warnings.showwarning

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        warnings.showwarning = warnings._showwarning

    def test_pr_122(self):
        """
        Feature implemented by @susundberg.

        Set the access time and modification time of a downloaded media
        according to its IG date.
        """
        looter = instaLooter.InstaLooter(
            self.tmpdir, profile='franz_ferdinand', template='{code}')
        # Test download_post
        info = looter.get_post_info('BY77tSfBnRm')
        looter.download_post('BY77tSfBnRm')
        stat = os.stat(os.path.join(self.tmpdir, 'BY77tSfBnRm.jpg'))
        self.assertEqual(stat.st_atime, info['date'])
        self.assertEqual(stat.st_mtime, info['date'])
        # Test download_pictures
        pic = next(m for m in looter.medias() if not m['is_video'])
        looter.download_pictures(media_count=1)
        stat = os.stat(os.path.join(self.tmpdir, '{}.jpg'.format(pic['code'])))
        self.assertEqual(stat.st_atime, pic['date'])
        self.assertEqual(stat.st_mtime, pic['date'])
        # Test download_videos
        vid = next(m for m in looter.medias() if m['is_video'])
        looter.download_videos(media_count=1)
        stat = os.stat(os.path.join(self.tmpdir, '{}.mp4'.format(vid['code'])))
        self.assertEqual(stat.st_atime, vid['date'])
        self.assertEqual(stat.st_mtime, vid['date'])


def setUpModule():
   warnings.simplefilter('ignore')

def tearDownModule():
   warnings.simplefilter(warnings.defaultaction)
