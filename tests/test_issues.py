import os
import unittest
import tempfile
import shutil
import glob
import datetime
import warnings
import piexif
import PIL.Image

import instaLooter



class TestInstaLooterResolvedIssues(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_issue_9(self):
        """
        Thanks to @kurtmaia for reporting this bug.

        Checks that adding metadata to pictures downloaded from a hashtag
        works as well.
        """
        instaLooter.main(["fluoxetine", self.tmpdir, "-n", "10", "-q", "--add-metadata"])
        for f in os.listdir(self.tmpdir):
            exif = piexif.load(os.path.join(self.tmpdir, f))
            self.assertTrue(exif['Exif']) # Date & Caption
            self.assertTrue(exif['0th'])  # Image creator

    def test_issue_12(self):
        """
        Feature request by @paramjitrohit.

        Allows downloading pictures and videos only within a timeframe.
        """
        looter = instaLooter.InstaLooter(self.tmpdir, profile="instagram")
        timeframe = (datetime.date(2016, 12, 17),)*2
        medias_in_timeframe = list(looter.medias(timeframe=timeframe))
        self.assertEqual(len(medias_in_timeframe), 3)

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

    def test_issue_6(self):
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


def setUpModule():
   warnings.simplefilter('ignore')

def tearDownModule():
   warnings.simplefilter(warnings.defaultaction)
