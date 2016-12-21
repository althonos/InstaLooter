#!/usr/bin/env python
# coding: utf-8
from __future__ import (
    absolute_import,
    unicode_literals,
)

import copy
import json
import os
import datetime
import progressbar
import random
import re
import requests
import six
import sys
import time
import bs4 as bs

from .worker import InstaDownloader
from .utils import get_times

PARSER = 'html.parser'



class InstaLooter(object):
    """A brutal Instagram looter that raids without API tokens.
    """

    _RX_SHARED_DATA = re.compile(r'window._sharedData = ({[^\n]*});')

    URL_HOME = "https://www.instagram.com/"
    URL_LOGIN = "https://www.instagram.com/accounts/login/ajax/"
    URL_LOGOUT = "https://www.instagram.com/accounts/logout/"

    def __init__(self, directory=None, profile=None, hashtag=None, add_metadata=False, get_videos=False, jobs=16):
        """Create a new looter instance.

        Keyword Arguments:
            directory (str, optional): where downloaded medias will be stored
                [default: None]
            profile (str, optional): a profile to download media from
                [default: None]
            hashtag (str, optional): a hashtag to download media from
                [default: None]
            add_metadata (bool, optional): Add date and comment metadata to
                the downloaded pictures [default: False]
            get_videos (bool, optional): Also get the videos from the given
                target [default: False]
            jobs (bool, optional): the number of parallel threads to use to
                download media (12 or more is advised to have a true parallel
                download of media files) [default: 16]
        """
        if profile is not None and hashtag is not None:
            raise ValueError("Give only a profile or an hashtag, not both !")

        if profile is not None:
            self.target = profile
            self._page_name = 'ProfilePage'
            self._section_name = 'user'
            self._base_url = "https://www.instagram.com/{}/"
        elif hashtag is not None:
            self.target = hashtag
            self._page_name = 'TagPage'
            self._section_name = 'tag'
            self._base_url = "https://www.instagram.com/explore/tags/{}/"
        else:
            self.target = None

        # Create self.directory if it doesn't exist.
        if directory is not None and not os.path.exists(directory):
            os.makedirs(directory)

        self.directory = directory
        self.add_metadata = add_metadata
        self.get_videos = get_videos
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
            'Host': 'www.instagram.com',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        })

    def __del__(self):
        if hasattr(self, 'session'):
            try:
                self.session.close()
            except ReferenceError:
                pass
        if hasattr(self, "_workers"):
            for worker in self._workers:
                worker.kill()
        if hasattr(self, '_pbar'):
            self._pbar.finish()

    def login(self, username, password):
        """Login with provided credentials.

        Arguments:
            username (str): the username to log in with
            password (str): the password to log in with

        (Code taken from LevPasha/instabot.py)
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

        login = self.session.post(self.URL_LOGIN, data=login_post, allow_redirects=True)
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
        """Log out from current session

        (Code taken from LevPasha/instabot.py)
        """
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

    def pages(self, media_count=None, with_pbar=False):
        """An iterator over the shared data of a profile or hashtag.

        Create a connection to www.instagram.com and use successive
        GET requests to load all pages of a profile. Each page contains
        12 media nodes, as well as metadata associated to the account.

        Arguments:
            media_count (int, optional): how many media to show before
                stopping [default: None]
            with_pbar (bool, optional): display a progress bar
                [default: False]

        Yields:
            dict: an dictionnary containing the page content deserialised
                from JSON to a Python dictionary
        """
        url = self._base_url.format(self.target)
        while True:
            res = self.session.get(url)
            data = self._get_shared_data(res)

            if media_count is None:
                media_count = data['entry_data'][self._page_name][0][self._section_name]['media']['count']

            if with_pbar:
                if not 'max_id' in url:  # First page: init pbar
                    self._init_pbar(1, media_count//12 + 1, 'Loading pages |')
                else:  # Other pages: update pbar
                    if self._pbar.value  == self._pbar.max_value:
                        self._pbar.max_value += 1
                    self._pbar.update(self._pbar.value+1)

            # First page: if user page, get metadata
            if not 'max_id' in url and self._section_name=="user":
                self.metadata = self._parse_metadata_from_profile_page(data)

            yield data

            media_info = data['entry_data'][self._page_name][0][self._section_name]['media']

            # Break if the page is private (no media to show) or if the last page was reached
            if not media_info['page_info']['has_next_page'] or not media_info["nodes"]:
                break
            else:
                url = '{}?max_id={}'.format(self._base_url.format(self.target), media_info['page_info']["end_cursor"])

    def medias(self, media_count=None, with_pbar=False, timeframe=None):
        """An iterator over the media nodes of a profile or hashtag.

        Using :obj:`InstaLooter.pages`, extract media nodes from each page
        and yields them successively.

        Arguments:
            media_count (int, optional): how many media to show before
                stopping [default: None]
            with_pbar (bool, optional): display a progress bar
                [default: False]
            timeframe (tuple, optional): a couple of datetime.date object
                specifying the date frame within which to yield medias
                (a None value can be given as well) [default: None]
                [format: (start, stop), stop older than start]
        """
        if timeframe is None: # Avoid checking timeframe every loop
            return self._timeless_medias(media_count=media_count, with_pbar=with_pbar)
        else:
            return self._timed_medias(media_count=media_count, with_pbar=with_pbar, timeframe=timeframe)

    def _timeless_medias(self, media_count=None, with_pbar=False):
        for page in self.pages(media_count=media_count, with_pbar=with_pbar):
                for media in page['entry_data'][self._page_name][0][self._section_name]['media']['nodes']:
                    yield media

    def _timed_medias(self, media_count=None, with_pbar=False, timeframe=None):
        start_time, end_time = get_times(timeframe)
        for page in self.pages(media_count=media_count, with_pbar=with_pbar):
            for media in page['entry_data'][self._page_name][0][self._section_name]['media']['nodes']:
                media_date = datetime.date.fromtimestamp(media['date'])
                if start_time >= media_date >= end_time:
                    yield media
                elif media_date < end_time:
                    return

    def download_pictures(self, media_count=None, with_pbar=False, timeframe=None):
        """Download all the pictures from provided target.

        Arguments:
            media_count (int, optional): how many media to download before
                stopping [default: None]
            with_pbar (bool, optional): display a progress bar
                [default: False]
            timeframe (tuple, optional): a couple of datetime.date object
                specifying the date frame within which to yield medias
                (a None value can be given as well) [default: None]
                [format: (start, stop), stop older than start]
        """
        self.download(media_count=media_count, with_pbar=with_pbar,
                      condition=lambda media: not media['is_video'],
                      timeframe=timeframe)

    def download_videos(self, media_count=None, with_pbar=False, timeframe=None):
        """Download all the videos from provided target.

        Arguments:
            media_count (int, optional): how many media to download before
                stopping [default: None]
            with_pbar (bool, optional): display a progress bar
                [default: False]
            timeframe (tuple, optional): a couple of datetime.date object
                specifying the date frame within which to yield medias
                (a None value can be given as well) [default: None]
                [format: (start, stop), stop older than start]
        """
        self.download(media_count=media_count, with_pbar=with_pbar,
                      condition=lambda media: media['is_video'],
                      timeframe=timeframe)

    def get_owner_info(self, code):
        """Get metadata about the owner of given post.

        Arguments:
            code (str): the code of the post (can be found in the url:
                https://www.instagram.com/p/<code>/) when looking at a
                specific media

        Returns:
            dict: an dictionnary containing the owner metadata deserialised
                from JSON to a Python dictionary
        """
        url = "https://www.instagram.com/p/{}/".format(code)
        res = self.session.get(url)
        data = self._get_shared_data(res)
        return data['entry_data']['PostPage'][0]['media']['owner']

    def download(self, media_count=None, with_pbar=False, timeframe=None, **kwargs):
        """Download all the medias from provided target.

        This method follwows the parameters given in the :obj:`__init__`
        method (profile or hashtag, directory, get_videos and add_metadata).

        Arguments:
            media_count (int, optional): how many media to download before
                stopping [default: None]
            with_pbar (bool, optional): display a progress bar
                [default: False]
            timeframe (tuple, optional): a couple of datetime.date object
                specifying the date frame within which to yield medias
                (a None value can be given as well) [default: None]
                [format: (start, stop), stop older than start]
        """
        if self.target is None:
            raise ValueError("No download target was specified during initialisation !")
        elif self.directory is None:
            raise ValueError("No directory was specified during initialisation !")

        self._init_workers()
        if not 'condition' in kwargs:
            condition = lambda media: (not media['is_video'] or self.get_videos)
        else:
            condition = kwargs.get('condition')
        medias_queued = self._fill_media_queue(media_count=media_count, with_pbar=with_pbar,
                                               condition=condition, timeframe=timeframe)
        if with_pbar:
            self._init_pbar(self.dl_count, medias_queued, 'Downloading |')
        self._poison_workers()
        self._join_workers(with_pbar=with_pbar)

    def download_post(self, code):
        """Download a single post referenced by its code.

        Arguments:
            code (str): the code of the post (can be found in the url:
                https://www.instagram.com/p/<code>/) when looking at a
                specific media
        """
        if self.directory is None:
            raise ValueError("No directory was specified during initialisation !")

        self._init_workers()
        url = "https://www.instagram.com/p/{}/".format(code)
        res = self.session.get(url)
        media = self._get_shared_data(res)['entry_data']['PostPage'][0]['media']
        self._medias_queue.put(media)
        self._poison_workers()
        self._join_workers()
        if self.add_metadata and not media['is_video']:
            self._add_metadata(photo_name, media)

    def _get_shared_data(self, res):
        soup = bs.BeautifulSoup(res.text, PARSER)
        script = soup.find('body').find('script', {'type': 'text/javascript'})
        return json.loads(self._RX_SHARED_DATA.match(script.text).group(1))

    def _fill_media_queue(self, media_count=None, with_pbar=False, condition=None, timeframe=None):
        medias_queued = 0
        for media in self.medias(media_count=media_count, with_pbar=with_pbar, timeframe=timeframe):
            if condition(media):
                media_url = media.get('display_src')
                media_basename = os.path.basename(media_url.split('?')[0])
                if not os.path.exists(os.path.join(self.directory, media_basename)):
                    self._medias_queue.put(media)
                    medias_queued += 1
            if media_count is not None and medias_queued >= media_count:
                break
        return medias_queued

    def _join_workers(self, with_pbar=False):
        while any(w.is_alive() for w in self._workers):
            if with_pbar and hasattr(self, '_pbar'):
                self._pbar.update(self.dl_count)
        if with_pbar and hasattr(self, '_pbar'):
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
        for _ in self._workers:
            self._medias_queue.put(None)

    def _parse_metadata_from_profile_page(self, data):
        user = data["entry_data"][self._page_name][0]["user"]
        metadata = {}
        for k, v in six.iteritems(user):
            metadata[k] = copy.copy(v)
        metadata['follows'] = metadata['follows']['count']
        metadata['followed_by'] = metadata['followed_by']['count']
        del metadata['media']['nodes']
        return metadata

    def is_logged_in(self):
        """Check if the current instance is logged in.
        """
        return self.csrftoken is not None



