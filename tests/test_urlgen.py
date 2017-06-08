import os
import glob
import shutil
import tempfile
import unittest
import PIL.Image

import instaLooter
from instaLooter.urlgen import resizer, thumbnail


class TestURLGen(unittest.TestCase):

    MEDIA_COUNT = 30

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_resizer(self):
        self.looter = instaLooter.InstaLooter(
            self.tmpdir, url_generator=resizer(320), profile="instagram"
        )
        self.looter.download(media_count=self.MEDIA_COUNT)

        for img_file in glob.iglob(os.path.join(self.tmpdir, "*.jpg")):
            with PIL.Image.open(img_file) as img:
                width, height = img.size
                self.assertEqual(max(width, height), 320)

    def test_thumbnail(self):
        self.looter = instaLooter.InstaLooter(
            self.tmpdir, url_generator=thumbnail, profile="therock"
        )
        self.looter.download(media_count=self.MEDIA_COUNT)

        for img_file in glob.iglob(os.path.join(self.tmpdir, "*.jpg")):
            with PIL.Image.open(img_file) as img:
                width, height = img.size
                self.assertEqual(width, height)
