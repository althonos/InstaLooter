#!/usr/bin/env python
# coding: utf-8
from __future__ import (
    absolute_import,
    unicode_literals,
)

import requests
import threading
import datetime
import os

try:
    import PIL.Image
    import piexif
except ImportError:
    PIL = None


class InstaDownloader(threading.Thread):

    def __init__(self, owner):
        super(InstaDownloader, self).__init__()
        self.medias = owner._medias_queue
        self.directory = owner.directory
        self.add_metadata = owner.add_metadata
        self.owner = owner
        self.session = requests.Session()
        self.session.cookies = self.owner.session.cookies
        self._killed = False

    def run(self):

        while not self._killed:
            media = self.medias.get()
            if media is None:
                break
            if not media['is_video']:
                self._download_photo(media)
            else:
                self._download_video(media)

            self.owner.dl_count += 1

    def _add_metadata(self, path, metadata):
        """
        """

        if PIL is not None:

            try:
                full_name = self.owner.metadata['full_name']
            except KeyError:
                full_name = self.owner.get_owner_info(metadata['code'])['full_name']


            img = PIL.Image.open(path)

            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st":{}, "thumbnail": None}

            exif_dict['0th'] = {
                piexif.ImageIFD.Artist: "Image creator, {}".format(full_name).encode('utf-8'),
            }

            exif_dict['1st'] = {
                piexif.ImageIFD.Artist: "Image creator, {}".format(full_name).encode('utf-8'),
            }

            exif_dict['Exif'] = {
                piexif.ExifIFD.DateTimeOriginal: datetime.datetime.fromtimestamp(metadata['date']).isoformat(),
                piexif.ExifIFD.UserComment: metadata.get('caption', '').encode('utf-8'),
            }

            img.save(path, exif=piexif.dump(exif_dict))

    def _download_photo(self, media):

        photo_url = media.get('display_src')
        photo_basename = os.path.basename(photo_url.split('?')[0])
        photo_name = os.path.join(self.directory, photo_basename)

        # save full-resolution photo
        self._dl(photo_url, photo_name)

        # put info from Instagram post into image metadata
        if self.add_metadata:
            self._add_metadata(photo_name, media)

    def _download_video(self, media):
        """
        """

        url = "https://www.instagram.com/p/{}/".format(media['code'])
        res = self.session.get(url)
        data = self.owner._get_shared_data(res)

        video_url = data["entry_data"]["PostPage"][0]["media"]["video_url"]
        video_basename = os.path.basename(video_url.split('?')[0])
        video_name = os.path.join(self.directory, video_basename)

        # save full-resolution photo
        self._dl(video_url, video_name)

    def _dl(self, source, dest):
        self.session.headers['Accept'] = '*/*'
        res = self.session.get(source)
        with open(dest, 'wb') as dest_file:
            for block in res.iter_content(1024):
                if block:
                    dest_file.write(block)

    def kill(self):
        self._killed = True

