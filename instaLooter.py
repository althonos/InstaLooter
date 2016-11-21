# coding: utf-8
import argparse
import gzip
import json
import threading
import os
import progressbar
import re
import six
import sys

from contextlib import closing
from bs4 import BeautifulSoup

try:
    from gi.repository import GExiv2
except ImportError:
    GExiv2 = None



class InstaDownloader(threading.Thread):

    def __init__(self, owner):
        super(InstaDownloader, self).__init__()
        self.medias = owner._medias_queue
        self.directory = owner.directory
        self.use_metadata = owner.use_metadata
        self.owner = owner

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
        Tag downloaded photos with metadata from associated Instagram post.

        If GExiv2 is not installed, do nothing.
        """
        if GExiv2 is not None:
            if metadata.get('caption') or metadata.get('date_time'):
                # todo: improve error handling
                try:
                    exif = GExiv2.Metadata(path)
                    if metadata.get('caption'):
                        try:
                            exif.set_comment(metadata.get('caption'))
                        except BaseException as be:
                            print("{} when setting comment on {}".format(type(be).__name__, path))
                    if metadata.get('date_time'):
                        try:
                            exif.set_date_time(metadata.get('date_time'))
                        except BaseException as be:
                            print("{} when setting datetime on {}".format(type(be).__name__, path))
                    exif.save_file()
                except BaseException as be:
                    pass

    def _download_photo(self, media):

        photo_url = media.get('display_src')
        photo_basename = os.path.basename(photo_url.split('?')[0])
        photo_name = os.path.join(self.directory, photo_basename)

        # save full-resolution photo
        with closing(six.moves.urllib.request.urlopen(photo_url)) as photo_con:
            with open(photo_name, 'wb') as img_file:
                img_file.write(photo_con.read())

        # put info from Instagram post into image metadata
        if self.use_metadata:
            self._add_metadata(photo_name, media)

    def _download_video(self, media):
        """
        Given source code for loaded Instagram page:
        - discover all video wrapper links
        - activate all links to load video url
        - extract and download video url
        """

        url = "https://www.instagram.com/p/{}/".format(media['code'])
        req = six.moves.urllib.request.Request(url, headers=self.owner._headers)
        con = six.moves.urllib.request.urlopen(req)

        if con.headers['Content-Encoding'] == 'gzip':
            con = gzip.GzipFile(fileobj=con)

        soup = BeautifulSoup(con.read().decode('utf-8'), 'lxml')
        script = soup.find('body').find('script', {'type':'text/javascript'})
        data = json.loads(self.owner._RX_SHARED_DATA.match(script.text).group(1))

        video_url = data["entry_data"]["PostPage"][0]["media"]["video_url"]
        video_basename = os.path.basename(video_url.split('?')[0])
        video_name = os.path.join(self.directory, video_basename)

        with closing(six.moves.urllib.request.urlopen(video_url)) as video_con:
            with open(video_name, 'wb') as video_file:
                video_file.write(video_con.read())

        # put info from Instagram post into image metadata
        if self.use_metadata:
            self._add_metadata(video_name, data["entry_data"]["PostPage"][0]["media"])

    def kill(self):
        self._killed = True




class InstaLooter(object):

    _RX_SHARED_DATA = re.compile(r'window._sharedData = ({[^\n]*});')

    def __init__(self, name, directory, num_to_download=None, log_level='info', use_metadata=True, get_videos=True, jobs=16):
        self.name = name
        self.directory = directory
        self.use_metadata = use_metadata
        self.get_videos = get_videos
        self.num_to_download=num_to_download or float("inf")
        self.jobs = jobs

        self.dl_count = 0

        self.metadata = {}

        self._cookies = None
        self._pbar = None
        self._headers =  {
            'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0",
            'Accept': 'text/html',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Host':'www.instagram.com',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        }
        self._setup_workers()

    def __del__(self):
        for worker in self._workers:
            worker.kill()

    def _setup_workers(self):
        self._shared_map = {}
        self._workers = []
        self._medias_queue = six.moves.queue.Queue()
        for _ in six.moves.range(self.jobs):
            worker = InstaDownloader(self)
            worker.start()
            self._workers.append(worker)

    def pages(self, pbar=True):

        url = "/{}/".format(self.name)
        with closing(six.moves.http_client.HTTPSConnection("www.instagram.com")) as con:
            while True:

                con.request("GET", url, headers=self._headers)
                res = con.getresponse()

                self._cookies = res.headers['Set-Cookie']
                self._headers['Cookie'] = self._cookies

                if res.headers['Content-Encoding'] == 'gzip':
                    res = gzip.GzipFile(fileobj=res)

                soup = BeautifulSoup(res.read().decode('utf-8'), 'lxml')
                script = soup.find('body').find('script', {'type':'text/javascript'})
                data = json.loads(self._RX_SHARED_DATA.match(script.text).group(1))

                media_count = data['entry_data']['ProfilePage'][0]['user']['media']['count']
                if pbar:
                    if not 'max_id' in url:
                        self._pbar = progressbar.ProgressBar(
                            min_value=1,
                            max_value=media_count//12 + (2 if media_count%12 else 1),
                            initial_value=1,
                            widgets=[
                                "Loading pages|",
                                progressbar.Percentage(),
                                '(', progressbar.SimpleProgress(), ')',
                                progressbar.Bar(),
                                progressbar.Timer(), ' ',
                                '|', progressbar.ETA(),
                            ]
                        )
                        self._pbar.start()
                    else:
                        self._pbar.update(self._pbar.value+1)

                yield data

                try:
                    max_id = data['entry_data']['ProfilePage'][0]['user']['media']['nodes'][-1]['id']
                    url = '/{}/?max_id={}'.format(self.name, max_id)
                except IndexError:
                    self._pbar.finish()
                    break

    def medias(self, pbar=True):
        for page in self.pages(pbar=pbar):
            for media in page['entry_data']['ProfilePage'][0]['user']['media']['nodes']:
                yield media

    def download_photos(self, pbar=True):
        photos_queued = 0
        for media in self.medias(pbar=pbar):
            if not media['is_video']:
                phot_url = media.get('display_src')
                photo_basename = os.path.basename(photo_url.split('?')[0])
                if not os.path.exists(os.path.join(self.directory, photo_basename)):
                    self._medias_queue.put(media)
                    photo_queued += 1
            if photos_queued >= self.num_to_download:
                break

        if pbar:
            self._pbar = progressbar.ProgressBar(
                min_value=1,
                max_value=photos_queued,
                initial_value=self.dl_count,
                widgets=[
                    "Downloading  |",
                    progressbar.Percentage(),
                    '(', progressbar.SimpleProgress(), ')',
                    progressbar.Bar(),
                    progressbar.Timer(), ' ',
                    '|', progressbar.ETA(),
                ]
            )
            self._pbar.start()

        for worker in self._workers:
            self._medias_queue.put(None)

        while any(w.is_alive() for w in self._workers):
            if pbar:
                self._pbar.update(self.dl_count)

    def download_videos(self, pbar=True):
        videos_queued = 0
        for media in self.medias(pbar=pbar):
            if media['is_video']:
                self._medias_queue.put(media)
                videos_queued += 1

                if videos_queued >= self.num_to_download:
                    break

        if pbar:
            self._pbar = progressbar.ProgressBar(
                min_value=1,
                max_value=videos_queued,
                initial_value=self.dl_count,
                widgets=[
                    "Downloading  |",
                    progressbar.Percentage(),
                    '(', progressbar.SimpleProgress(), ')',
                    progressbar.Bar(),
                    progressbar.Timer(), ' ',
                    '|', progressbar.ETA(),
                ]
            )
            self._pbar.start()



        for worker in self._workers:
            self._medias_queue.put(None)

        while any(w.is_alive() for w in self._workers):
            if pbar:
                self._pbar.update(self.dl_count)

    def download(self, pbar=True):
        medias_queued = 0
        for media in self.medias(pbar=pbar):
            if not media['is_video'] or self.get_videos:
                media_url = media.get('display_src')
                media_basename = os.path.basename(media_url.split('?')[0])
                if not os.path.exists(os.path.join(self.directory, media_basename)):
                    self._medias_queue.put(media)
                    medias_queued += 1
            if medias_queued >= self.num_to_download:
                break

        if pbar:
            self._pbar = progressbar.ProgressBar(
                min_value=1,
                max_value=medias_queued,
                initial_value=self.dl_count,
                widgets=[
                    "Downloading  |",
                    progressbar.Percentage(),
                    '(', progressbar.SimpleProgress(), ')',
                    progressbar.Bar(),
                    progressbar.Timer(), ' ',
                    '|', progressbar.ETA(),
                ]
            )
            self._pbar.start()

        for worker in self._workers:
            self._medias_queue.put(None)

        while any(w.is_alive() for w in self._workers):
            if pbar:
                self._pbar.update(self.dl_count)

        self._pbar.finish()


def main(args=sys.argv):
    # parse arguments
    parser = argparse.ArgumentParser(description='InstaLooter')
    parser.add_argument('username', help='Instagram username')
    parser.add_argument('directory', help='Where to save the images')
    parser.add_argument('-n', '--num-to-download',
                        help='Number of posts to download', type=int)
    parser.add_argument('-m', '--add_metadata',
                        help=("Add metadata (caption/date) from Instagram "
                              "post into downloaded images' exif tags "
                              "(requires GExiv2 python module)"),
                        action='store_true', dest='use_metadata')
    parser.add_argument('-v', '--get_videos',
                        help="Download videos",
                        action='store_true', dest='get_videos')
    parser.add_argument('-j', '--jobs',
                        help="Number of concurrent threads to use",
                        action='store', dest='jobs',
                        type=int, default=64)
    parser.add_argument('-q', '--quiet',
                        help="Do not display any output",
                        action='store_true')

    args = parser.parse_args()

    looter = InstaLooter(name=args.username,
                         directory=os.path.expanduser(args.directory),
                         num_to_download=args.num_to_download,
                         use_metadata=args.use_metadata,
                         get_videos=args.get_videos,
                         jobs=args.jobs)

    try:
        looter.download(pbar=not args.quiet)
    except KeyboardInterrupt:
        looter.__del__()

if __name__=="__main__":
    main(sys.argv)
