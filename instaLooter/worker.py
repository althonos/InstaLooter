#!/usr/bin/env python
# coding: utf-8
from __future__ import (
    absolute_import,
    unicode_literals,
)

import requests
import contextlib
import threading
import datetime
import os
import re


try:
    import PIL.Image
    import piexif
except ImportError:
    PIL = None


class InstaDownloader(threading.Thread):

    _NO_RESIZE_RX = re.compile(r'(/p[0-9]*x[0-9]*)')

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
        """
        """
        photo_url = self._NO_RESIZE_RX.sub('', media.get('display_src'))
        photo_name = os.path.join(self.directory, self.owner._make_filename(media))

        # save full-resolution photo
        self._dl(photo_url, photo_name)

        # put info from Instagram post into image metadata
        if self.add_metadata:
            self._add_metadata(photo_name, media)

    def _download_video(self, media):
        """
        """
        url = "https://www.instagram.com/p/{}/".format(media['code'])
        with contextlib.closing(self.session.get(url)) as res:
            data = self.owner._get_shared_data(res)['entry_data']['PostPage'][0]['media']

        video_url = data["video_url"]
        video_basename = os.path.basename(video_url.split('?')[0])
        video_name = os.path.join(self.directory, self.owner._make_filename(data))

        # save video
        self._dl(video_url, video_name)

    def _dl(self, source, dest):
        self.session.headers['Accept'] = '*/*'
        with contextlib.closing(self.session.get(source)) as res:
            with open(dest, 'wb') as dest_file:
                for block in res.iter_content(1024):
                    if block:
                        dest_file.write(block)

    def kill(self):
        self._killed = True
