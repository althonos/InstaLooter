# coding: utf-8

__author__ = "althonos"
__author_email__ = "martin.larralde@ens-cachan.fr"
__version__ = "0.2.2"

import argparse
import copy
import datetime
import gzip
import json
import os
import progressbar
import random
import re
import requests
import six
import sys
import threading
import time

from contextlib import closing
from bs4 import BeautifulSoup

try:
    import PIL.Image
    import piexif
except ImportError:
    PIL = None

try:
    import lxml
    PARSER = 'lxml'
except ImportError:
    PARSER = 'html'

class InstaDownloader(threading.Thread):

    def __init__(self, owner):
        super(InstaDownloader, self).__init__()
        self.medias = owner._medias_queue
        self.directory = owner.directory
        self.use_metadata = owner.use_metadata
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

            img = PIL.Image.open(path)

            exif_dict = {"0th":{}, "Exif":{}, "GPS":{}, "1st":{}, "thumbnail":None}

            exif_dict['0th'] = {
                piexif.ImageIFD.Artist: "Image creator, {}".format(self.owner.metadata['full_name']),
            }

            exif_dict['1st'] = {
                piexif.ImageIFD.Artist: "Image creator, {}".format(self.owner.metadata['full_name']),
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
        if self.use_metadata:
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




class InstaLooter(object):

    _RX_SHARED_DATA = re.compile(r'window._sharedData = ({[^\n]*});')
    _RX_CSRFTOKEN = re.compile(r'csrftoken=([^;]*);')
    _RX_CSRFTOKEN_JSON = re.compile(rb'"csrf_token": "([a-zA-Z0-9]*)"')

    URL_HOME = "https://www.instagram.com/"
    URL_LOGIN = "https://www.instagram.com/accounts/login/ajax/"
    URL_LOGOUT ="https://www.instagram.com/accounts/logout/"

    def __init__(self, name, directory, num_to_download=None, log_level='info', use_metadata=True, get_videos=True, jobs=16):
        self.name = name
        self.directory = directory
        self.use_metadata = use_metadata
        self.get_videos = get_videos
        self.num_to_download=num_to_download or float("inf")
        self.jobs = jobs


        self.session = requests.Session()
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"
        self.csrftoken = None

        self.dl_count = 0
        self.metadata = {}

        self._workers = []


        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Host':'www.instagram.com',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        })

    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()
        for worker in self._workers:
            worker.kill()
        if hasattr(self, '_pbar'):
            self._pbar.finish()

    def login(self, username, password):
        """Log in with provided credentials.

        Code taken from LevPasha/instabot.py
        """
        self.session.cookies.update({
            'sessionid': '',
            'mid': '',
            'ig_pr': '1',
            'ig_vw': '1920',
            'csrftoken': '',
            's_network': '',
            'ds_user_id': ''
        })

        login_post = {'username': username,
                      'password': password}

        self.session.headers.update({
            'Origin': self.URL_HOME,
            'Referer': self.URL_HOME,
            'X-Instragram-AJAX': '1',
            'X-Requested-With': 'XMLHttpRequest',
        })

        res = self.session.get(self.URL_HOME)
        self.session.headers.update({'X-CSRFToken': res.cookies['csrftoken']})
        time.sleep(5 * random.random())

        login = self.session.post(self.URL_LOGIN, data = login_post, allow_redirects=True)
        self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.csrftoken = login.cookies['csrftoken']

        if login.status_code != 200:
            self.csrftoken = None
            raise SystemError("Login error: check your connection")
        else:
            r = self.session.get(self.URL_HOME)
            if r.text.find(username) == -1:
                raise ValueError('Login error: check your login data')

    def logout(self):
        logout_post = {'csrfmiddlewaretoken': self.csrftoken}
        logout = self.session.post(self.URL_LOGOUT, data=logout_post)
        self.csrftoken = None

    def _init_workers(self):
        """Initialize a pool of workers to download files
        """
        self._shared_map = {}
        self._workers = []
        self._medias_queue = six.moves.queue.Queue()
        for _ in six.moves.range(self.jobs):
            worker = InstaDownloader(self)
            worker.start()
            self._workers.append(worker)

    def pages(self, with_pbar=False):
        """An iterator over the shared data of the instagram profile

        Create a connection to www.instagram.com and use successive
        GET requests to load all pages of a profile.
        Each page contains 12 media nodes, as well as metadata associated
        to the account.

        Arguments:
            -

        Yields:
            dict: an dictionnary containing
        """


        url = "https://www.instagram.com/{}/".format(self.name)
        #with closing(six.moves.http_client.HTTPSConnection("www.instagram.com")) as con:
        while True:

            res = self.session.get(url)
            data = self._get_shared_data(res)

            if self.num_to_download == float('inf'):
                media_count = data['entry_data']['ProfilePage'][0]['user']['media']['count']
            else:
                media_count = self.num_to_download

            if with_pbar:
                if not 'max_id' in url: # First page: init pbar
                    self._init_pbar(1, media_count//12 + 1, 'Loading pages |')
                else: # Other pages: update pbar
                    if self._pbar.value < self._pbar.max_value:
                        self._pbar.update(self._pbar.value+1)

            if not 'max_id' in url:
                self._parse_metadata(data)

            yield data

            try:
                max_id = data['entry_data']['ProfilePage'][0]['user']['media']['nodes'][-1]['id']
                url = 'https://www.instagram.com/{}/?max_id={}'.format(self.name, max_id)
            except IndexError:
                break

    def medias(self, with_pbar=False):
        """
        """
        for page in self.pages(with_pbar=with_pbar):
            for media in page['entry_data']['ProfilePage'][0]['user']['media']['nodes']:
                yield media

    def download_photos(self, with_pbar=False):
        self.download(with_pbar=with_pbar, condition=lambda media: not media['is_video'])

    def download_videos(self, with_pbar=False):
        self.download(with_pbar=with_pbar, condition=lambda media: media['is_video'])

    def download(self, with_pbar=False, condition=None):
        self._init_workers()
        if condition is None:
            condition = lambda media: (not media['is_video'] or self.get_videos)
        medias_queued = self._fill_media_queue(with_pbar=with_pbar, condition=condition)
        if with_pbar:
            self._init_pbar(self.dl_count, medias_queued, 'Downloading |')
        self._poison_workers()
        self._join_workers(with_pbar=with_pbar)

    def _get_shared_data(self, res):
        soup = BeautifulSoup(res.text, PARSER)
        script = soup.find('body').find('script', {'type':'text/javascript'})
        return json.loads(self._RX_SHARED_DATA.match(script.text).group(1))

    def _fill_media_queue(self, with_pbar, condition):
        medias_queued = 0
        for media in self.medias(with_pbar=with_pbar):
            if condition(media):
                media_url = media.get('display_src')
                media_basename = os.path.basename(media_url.split('?')[0])
                if not os.path.exists(os.path.join(self.directory, media_basename)):
                    self._medias_queue.put(media)
                    medias_queued += 1
            if medias_queued >= self.num_to_download:
                break
        return medias_queued

    def _join_workers(self, with_pbar=False):
        while any(w.is_alive() for w in self._workers):
            if with_pbar:
                self._pbar.update(self.dl_count)
        self._pbar.update(self.dl_count)

    def _init_pbar(self, ini_val, max_val, label):
        self._pbar = progressbar.ProgressBar(
            min_value=0,
            max_value=max_val,
            initial_value=ini_val,
            widgets=[
                label,
                progressbar.Percentage(),
                '(', progressbar.SimpleProgress(), ')',
                progressbar.Bar(),
                progressbar.Timer(), ' ',
                '|', progressbar.ETA(),
            ]
        )
        self._pbar.start()

    def _poison_workers(self):
        for worker in self._workers:
            self._medias_queue.put(None)

    def _parse_metadata(self, data):
        user = data["entry_data"]["ProfilePage"][0]["user"]
        for k,v in six.iteritems(user):
            self.metadata[k] = copy.copy(v)
        self.metadata['follows'] = self.metadata['follows']['count']
        self.metadata['followed_by'] = self.metadata['followed_by']['count']
        del self.metadata['media']['nodes']

    def is_logged_in(self):
        return self.csrftoken is not None


def main(args=sys.argv):
    # parse arguments
    parser = argparse.ArgumentParser(
        description='%(prog)s: Another API-less Instagram pictures and videos downloader.',
        usage='%(prog)s [options] username directory',
    )
    parser.add_argument('username', help='the instagram account to download posts from')
    parser.add_argument('directory', help='the directory to download files into')
    parser.add_argument('--version', action='version', version="%(prog)s ("+__version__+")")
    parser.add_argument('-n', type=int, metavar='NUM', dest='num_to_download',
                        help=("number of new posts to download "
                              "(if not specified all posts are downloaded)")),
    parser.add_argument('-m', '--add-metadata',
                        help=("add date and caption metadata to downloaded pictures "
                              "(requires PIL/Pillow and piexif)"),
                        action='store_true', dest='use_metadata')
    parser.add_argument('-v', '--get-videos',
                        help="also download videos",
                        action='store_true', dest='get_videos')
    parser.add_argument('-j', '--jobs', metavar='JOBS',
                        help=("the number of parallel threads to use to download files "
                              "[default: 16]"),
                        action='store', dest='jobs',
                        type=int, default=16)
    parser.add_argument('-q', '--quiet',
                        help="do not produce any output",
                        action='store_true')

    args = parser.parse_args()

    looter = InstaLooter(name=args.username,
                         directory=os.path.expanduser(args.directory),
                         num_to_download=args.num_to_download,
                         use_metadata=args.use_metadata,
                         get_videos=args.get_videos,
                         jobs=args.jobs)

    try:
        looter.download(with_pbar=not args.quiet)
    except KeyboardInterrupt:
        looter.__del__()

if __name__=="__main__":
    main(sys.argv)
