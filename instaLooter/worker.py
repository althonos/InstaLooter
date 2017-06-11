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
import six

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
            try:
                media = self.medias.get(timeout=1)
                if media is None:
                    break
                elif media.get('is_video'):
                    self._download_video(media)
                else:
                    self._download_photo(media)
                with self.owner.dl_count_lock:
                    self.owner.dl_count += 1
            except six.moves.queue.Empty:
                pass


    def _add_metadata(self, path, metadata):
        """Add some metadata to the picture located at `path`.
        """

        if PIL is not None:

            try:
                full_name = self.owner.metadata['full_name']
            except KeyError:
                full_name = self.owner.get_owner_info(
                    metadata.get('shortcode') or metadata['code']
                )['full_name']


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
        """Download a picture from a media dictionnary.
        """
        photo_url = self.owner.url_generator(media)

        if not isinstance(photo_url, six.string_types):
            raise RuntimeError('The "custom_photo_url" option must return a string !')

        photo_name = os.path.join(self.directory, self.owner._make_filename(media))

        # save full-resolution photo
        self._dl(photo_url, photo_name)

        # put info from Instagram post into image metadata
        if self.add_metadata:
            self._add_metadata(photo_name, media)


    def _download_video(self, media):
        """Download a video from a media dictionnary.
        """
        url = "https://www.instagram.com/p/{}/".format(media.get('shortcode') or media['code'])

        if "video_url" not in media:
            with contextlib.closing(self.session.get(url)) as res:
                # data = self.owner._get_shared_data(res)['entry_data']['PostPage'][0]['media']
                data = self.owner._get_shared_data(res)['entry_data']['PostPage'][0]['graphql']['shortcode_media']
        else:
            data = media

        video_url = data["video_url"]
        #video_basename = os.path.basename(video_url.split('?')[0])
        video_name = os.path.join(self.directory, self.owner._make_filename(data))

        # save video
        self._dl(video_url, video_name)

    def _dl(self, source, dest):
        """Download a file located at `source` to `dest`.
        """
        self.session.headers['Accept'] = '*/*'
        with contextlib.closing(self.session.get(source)) as res:
            with open(dest, 'wb') as dest_file:
                for block in res.iter_content(1024):
                    if block:
                        dest_file.write(block)

    def kill(self):
        """Kill the Thread.

        This method actually performs a soft kill, it just
        forces the Thread to break the infinite loop. If the Thread
        is currently downloading a file, it will first finish the
        download before exiting.
        """
        self._killed = True
