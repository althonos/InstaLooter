import unittest
import tempfile
import shutil

import instaLooter



class TestInstaLooterCommandLineInterface(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_issue_12(self):
        """
        Feature request by @paramjitrohit.
        """
        looter = instaLooter.InstaLooter(self.tmpdir, profile="instagram")
        timeframe = (datetime.date(2016, 12, 17),)*2
        medias_in_timeframe = list(looter.medias(timeframe=timeframe))
        self.assertEqual(len(medias_in_timeframe), 3)

    def test_issue_19(self):
        """
        Thanks to @emijawdo for issue report.
        """
        initial_dir = os.getcwd()
        os.chdir(self.tmpdir)
        instaLooter.main(["mysteryjets", "-n", "10", "-q"])
        self.assertEqual(len(os.listdir(self.tmpdir)), 10)
        os.chdir(initial_dir)

    def test_issue_14(self):
        """
        Feature request by @JFLarsen.
        """
        instaLooter.main(["mysteryjets", self.tmpdir, "-n", "10", "-q", "-T", "{username}.{date}.{id}"])
        for f in os.listdir(self.tmpdir):
            self.assertTrue(f.startswith('mysteryjets'))

    def test_issue_6(self):
        """
        """
        looter = instaLooter.InstaLooter(self.tmpdir, profile="tldr")
        with self.assertRaises(StopIteration):
            next(looter.medias())

    def test_issue_15(self):
        """
        Feature request by @MohamedIM.
        """
        looter = instaLoter.InstaLooter(self.tmpdir, profile="instagram")
        looter.download_videos(media_count=1)
        video_file = next(glob.glob(os.path.join(self.tmpdir, '*.mp4')))
        mtime = os.stat(video_file).st_mtime
        looter.download_videos(media_count=1, new_only=True)
        self.assertEqual(mtime, os.stat(video_file).st_mtime)
