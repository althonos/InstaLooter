#!/usr/bin/env python
# coding: utf-8
from __future__ import (
    absolute_import,
    unicode_literals,
)

import atexit
import copy
import json
import os
import datetime
import progressbar
import random
import re
import warnings
import threading
import requests
import six
import time
import tempfile
import bs4 as bs

from .urlgen import default
from .worker import InstaDownloader
from .utils import get_times, save_cookies, load_cookies

PARSER = 'html.parser'


class InstaLooter(object):
    """A brutal Instagram looter that raids without API tokens.
    """

    _RX_SHARED_DATA = re.compile(r'window._sharedData = ({[^\n]*});')
    _RX_TEMPLATE = re.compile(r'{([a-zA-Z]*)}')
    _RX_CODE_URL = re.compile(r'p/([^/]*)')

    URL_HOME = "https://www.instagram.com/"
    URL_LOGIN = "https://www.instagram.com/accounts/login/ajax/"
    URL_LOGOUT = "https://www.instagram.com/accounts/logout/"

    COOKIE_FILE = os.path.join(tempfile.gettempdir(), "instaLooter", "cookies.txt")

    _TEMPLATE_MAP = {
        'id': lambda m: m.get('id'),
        'code': lambda m: m.get('code') or m.get('shortcode'),
        'ownerid': lambda m: m.get('owner', dict()).get('id'),
        'username': lambda m: m.get('owner', dict()).get('username'),
        'fullname': lambda m: m.get('owner', dict()).get('full_name'),
        'datetime': lambda m: ("{0.year}-{0.month}-{0.day} {0.hour}h{0.minute}m{0.second}"
            "s{0.microsecond}".format(datetime.datetime.fromtimestamp(m['date'])))
            if 'date' in m else None,
        'date': lambda m: datetime.date.fromtimestamp(m['date'])
            if 'date' in m else None,
        'width': lambda m: m.get('dimensions', dict()).get('width'),
        'heigth': lambda m: m.get('dimensions', dict()).get('height'),
        'likescount': lambda m: m.get('likes', dict()).get('count'),
        'commentscount': lambda m: m.get('comments', dict()).get('count'),
        'display_src': lambda m: m.get('display_src'),
        'video_url': lambda m: m.get('video_url'),
    }

    _OWNER_MAP = {}

    def __init__(self, directory=None, profile=None, hashtag=None,
                add_metadata=False, get_videos=False, videos_only=False,
                jobs=16, template="{id}", url_generator=default):
        """Create a new looter instance.

        Keyword Arguments:
            directory (`str`): where downloaded medias will be stored
                **[default: None]**
            profile (`str`): a profile to download media from
                **[default: None]**
            hashtag (`str`): a hashtag to download media from
                **[default: None]**
            add_metadata (`bool`): Add date and comment metadata to
                the downloaded pictures. **[default: False]**
            get_videos (`bool`): Also get the videos from the given
                target **[default: False]**
            videos_only (`bool`): Only download videos (implies
                ``get_videos=True``). **[default: False]**
            jobs (`bool`): the number of parallel threads to use to
                download media (12 or more is advised to have a true parallel
                download of media files) **[default: 16]**
            url_generator (`function`): a callable that takes a media
                dictionnary as argument and returs the URL it should
                download the picture from. The default tries to get
                the best available size.
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

        self.template = template
        self._required_template_keys = self._RX_TEMPLATE.findall(template)

        self.url_generator = url_generator
        if not callable(url_generator):
            raise ValueError("url_generator must be a callable !")

        self.directory = directory
        self.add_metadata = add_metadata
        self.get_videos = get_videos or videos_only
        self.videos_only = videos_only
        self.jobs = jobs

        self.session = requests.Session()
        self.session.cookies = six.moves.http_cookiejar.LWPCookieJar(self.COOKIE_FILE)
        load_cookies(self.session)

        self.user_agent = ("Mozilla/5.0 (Windows NT 10.0; WOW64; "  # seems legit
                           "rv:50.0) Gecko/20100101 Firefox/50.0")

        self.dl_count = 0
        self.metadata = {}
        self._workers = []
        self.dl_count_lock = threading.Lock()

        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Host': 'www.instagram.com',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        })

        atexit.register(self.__del__)

    def __del__(self):
        if hasattr(self, 'session'):
            try:
                self.session.close()
            except ReferenceError:
                pass
        if hasattr(self, "_workers"):
            for worker in self._workers:
                worker.kill()

    def __length_hint__(self):
        try:
            data = next(self.pages())['entry_data'][self._page_name][0]
            length = data[self._section_name]['media']['count']
        except (KeyError, StopIteration):
            length = 0
        return length

    def login(self, username, password):
        """Login with provided credentials.

        Arguments:
            username (`str`): the username to log in with
            password (`str`): the password to log in with

        .. note::

            Code taken from LevPasha/instabot.py
        """
        # self.session.cookies.update({
        #     'sessionid': '',
        #     'mid': '',
        #     'ig_pr': '1',
        #     'ig_vw': '1920',
        #     'csrftoken': '',
        #     's_network': '',
        #     'ds_user_id': ''
        # })

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
        time.sleep(5 * random.random()) # nosec

        login = self.session.post(self.URL_LOGIN, data=login_post, allow_redirects=True)
        self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.csrftoken = login.cookies['csrftoken']
        # save_cookies(self.session, 'cookies.txt')

        if login.status_code == 200:
            r = self.session.get(self.URL_HOME)
            if r.text.find(username) == -1:
                raise ValueError('Login error: check your login data')
            save_cookies(self.session)
        else:
            raise SystemError("Login error: check your connection")

    def logout(self):
        """Log out from current session.

        .. note::

            Code taken from LevPasha/instabot.py
        """
        logout_post = {'csrfmiddlewaretoken': self.csrftoken}
        logout = self.session.post(self.URL_LOGOUT, data=logout_post)
        self.csrftoken = None
        if os.path.isfile(self.COOKIE_FILE):
            os.remove(self.COOKIE_FILE)

    def _init_workers(self):
        """Initialize a pool of workers to download files.
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
            media_count (`int`): how many media to show before
                stopping **[default: None]**
            with_pbar (`bool`): display a progress bar. **[default: False]**

        Yields:
            `dict`: the page content deserialised from JSON
        """
        url = self._base_url.format(self.target)
        current_page = 0
        while True:
            current_page += 1
            res = self.session.get(url)
            data = self._get_shared_data(res)

            try:
                media_info = data['entry_data'][self._page_name][0][self._section_name]['media']
            except KeyError:
                warnings.warn("Could not find page of user: {}".format(self.target), stacklevel=1)
                return

            if media_count is None:
                media_count = data['entry_data'][self._page_name][0][self._section_name]['media']['count']

            if with_pbar and media_info['page_info']['has_next_page'] and media_info["nodes"]:
                if 'max_id' not in url:  # First page: init pbar
                    self._init_pbar(1, media_count//12 + 1, 'Loading pages |')
                else:  # Other pages: update pbar
                    if self._pbar.value  == self._pbar.max_value:
                        self._pbar.max_value += 1
                    self._pbar.update(self._pbar.value+1)

            # First page: if user page, get metadata
            if 'max_id' not in url and self._section_name=="user":
                self.metadata = self._parse_metadata_from_profile_page(data)

            yield data

            # Break if the page is private (no media to show) or if the last page was reached
            if not media_info['page_info']['has_next_page']:
                break
            elif not media_info["nodes"]:
                if self._section_name == "tag":
                    warnings.warn("#{} has no medias to show.".format(self.target))
                elif self.is_logged_in() is None:
                    warnings.warn("Profile {} is private, retry after logging in.".format(self.target))
                else:
                    warnings.warn("Profile {} is private, and you are not following it.".format(self.target))
                break
            else:
                url = '{}?max_id={}'.format(self._base_url.format(self.target), media_info['page_info']["end_cursor"])

    def medias(self, media_count=None, with_pbar=False, timeframe=None):
        """An iterator over the media nodes of a profile or hashtag.

        Using :obj:`InstaLooter.pages`, extract media nodes from each page
        and yields them successively.

        Arguments:
            media_count (`int`): how many media to show before
                stopping **[default: None]**
            with_pbar (`bool`): display a progress bar **[default: False]**
            timeframe (`tuple`): a couple of datetime.date object
                specifying the date frame within which to yield medias
                (a None value can be given as well) **[default: None]**
                **[format: (start, stop), stop older than start]**
        """
        if timeframe is None: # Avoid checking timeframe every loop
            return self._timeless_medias(media_count=media_count, with_pbar=with_pbar)
        else:
            return self._timed_medias(media_count=media_count, with_pbar=with_pbar, timeframe=timeframe)

    def _timeless_medias(self, media_count=None, with_pbar=False):
        seen = set()
        for page in self.pages(media_count=media_count, with_pbar=with_pbar):
            for media in page['entry_data'][self._page_name][0][self._section_name]['media']['nodes']:
                if media['id'] in seen:
                    return
                yield media
                seen.add(media['id'])

    def _timed_medias(self, media_count=None, with_pbar=False, timeframe=None):
        seen = set()
        start_time, end_time = get_times(timeframe)
        for page in self.pages(media_count=media_count, with_pbar=with_pbar):
            for media in page['entry_data'][self._page_name][0][self._section_name]['media']['nodes']:
                media_date = datetime.date.fromtimestamp(media['date'])
                if start_time >= media_date >= end_time:
                    if media['id'] in seen:
                        return
                    yield media
                    seen.add(media['id'])
                elif media_date < end_time:
                    return

    def download_pictures(self, **kwargs):#media_count=None, with_pbar=False, timeframe=None, new_only=False):
        """Download all the pictures from provided target.

        Keyword Arguments:
            media_count (`int`): how many media to download before
                stopping **[default: None]**
            with_pbar (`bool`): display a progress bar **[default: False]**
            timeframe (`tuple`): a couple of datetime.date object
                specifying the date frame within which to yield medias
                (a None value can be given as well) **[default: None]**
                **[format: (start, stop), stop older than start]**
            new_only (`bool`):
                stop looking for new medias if old ones are found in the
                destination directory **[default: False]**
        """
        self.download(_condition=lambda media: not media['is_video'], **kwargs)

    def download_videos(self, **kwargs):#media_count=None, with_pbar=False, timeframe=None):
        """Download all the videos from provided target.

        Keyword Arguments:
            media_count (`int`): how many media to download before
                stopping **[default: None]**
            with_pbar (`bool`): display a progress bar **[default: False]**
            timeframe (`tuple`): a couple of datetime.date object
                specifying the date frame within which to yield medias
                (a None value can be given as well) **[default: None]**
                **[format: (start, stop), stop older than start]**
            new_only (`bool`):
                stop looking for new medias if old ones are found in the
                destination directory **[default: False]**
        """
        self.download(_condition=lambda media: media['is_video'], **kwargs)

    def get_owner_info(self, code):
        """Get metadata about the owner of given post.

        Arguments:
            code (`str`): the code of the post (can be found in the url:
                ``https://www.instagram.com/p/<code>/``) when looking at a
                specific media

        Returns:
            `dict`: the owner metadata deserialised from JSON
        """
        url = "https://www.instagram.com/p/{}/".format(code)
        res = self.session.get(url)
        data = self._get_shared_data(res)
        return data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['owner']

    def download(self, **kwargs):
        """Download all the medias from provided target.

        This method follwows the parameters given in the :obj:`__init__`
        method (profile or hashtag, directory, get_videos, videos_only
        and add_metadata).

        Keyword Arguments:
            media_count (`int`): how many media to download before
                stopping **[default: None]**
            with_pbar (`bool`): display a progress bar
                **[default: False]**
            timeframe (`tuple`): a couple of :obj:`datetime.date` object
                specifying the date frame within which to yield medias
                (a None value can be given as well) **[default: None]**
                **[format: (start, stop), stop older than start]**
            new_only (`bool`):
                stop looking for new medias if old ones are found in the
                destination directory **[default: False]**
        """
        # extract the parameters here to avoid having a too heavy
        # function signature
        media_count = kwargs.get('media_count', None)
        with_pbar = kwargs.get('with_pbar', False)
        timeframe = kwargs.get('timeframe', None)
        new_only = kwargs.get('new_only', False)

        if self.target is None:
            raise ValueError("No download target was specified during initialisation !")
        elif self.directory is None:
            raise ValueError("No directory was specified during initialisation !")

        self._init_workers()
        if '_condition' not in kwargs:
            if self.videos_only:
                condition = lambda media: media['is_video']
            elif not self.get_videos:
                condition = lambda media: not media['is_video']
            else:
                condition = lambda media: True
        else:
            condition = kwargs.get('_condition')

        medias_queued = self._fill_media_queue(
            media_count=media_count, with_pbar=with_pbar,
            condition=condition, timeframe=timeframe,
            new_only=new_only
        )

        if medias_queued == 0:
            warnings.warn("No {}medias found.".format('new ' if new_only else ''))
        elif with_pbar:
            self._init_pbar(self.dl_count, medias_queued, 'Downloading |')
        self._poison_workers()
        self._join_workers(with_pbar=with_pbar)

    def download_post(self, code):
        """Download a single post referenced by its code.

        Arguments:
            code (`str`): the code of the post (can be found in the url:
                ``https://www.instagram.com/p/<code>/``) when looking
                at a specific media.
        """
        if self.directory is None:
            raise ValueError("No directory was specified during initialisation !")

        self._init_workers()
        media = self.get_post_info(code)

        if media.get('__typename') == "GraphSidecar":
            self._add_sidecars_to_queue(media, lambda m: True, None, 0, False)
        else:
            self._add_media_to_queue(media, lambda m: True, None, 0, False)

        self._poison_workers()
        self._join_workers()
        if self.add_metadata and not media['is_video']:
            self._add_metadata(
                os.path.join(self.directory, self._make_filename(media)),
                media
            )

    def get_post_info(self, code):
        """Get info about a single post referenced by its code

        Arguments:
            code (`str`): the code of the post (can be found in the url:
                ``https://www.instagram.com/p/<code>/``) when looking
                at a specific media.
        """
        url = "https://www.instagram.com/p/{}/".format(code)
        res = self.session.get(url)
        # media = self._get_shared_data(res)['entry_data']['PostPage'][0]['media']
        media = self._get_shared_data(res)['entry_data']['PostPage'][0]['graphql']['shortcode_media']
        # Fix renaming of attributes
        media.setdefault('code', media.get('shortcode'))
        media.setdefault('date', media.get('taken_at_timestamp'))
        media.setdefault('display_src', media.get('display_url'))
        media.setdefault('likes', media['edge_media_preview_like'])
        media.setdefault('comments', media['edge_media_to_comment'])
        return media

    @classmethod
    def _extract_code_from_url(cls, url):
        result = cls._RX_CODE_URL.search(url)
        if result is None:
            raise ValueError("Invalid post url: {}".format(url))
        else:
            return result.group(1)

    def _get_shared_data(self, res):
        soup = bs.BeautifulSoup(res.text, PARSER)
        script = soup.find('body').find('script', {'type': 'text/javascript'})
        return json.loads(self._RX_SHARED_DATA.match(script.text).group(1))

    def _fill_media_queue(self, media_count=None, with_pbar=False, condition=None, timeframe=None, new_only=False):
        medias_queued = 0
        condition = condition or (lambda media: self.get_videos or not media['is_video'])
        for media in self.medias(media_count=media_count, with_pbar=with_pbar, timeframe=timeframe):
            medias_queued, stop = self._add_media_to_queue(media, condition, media_count, medias_queued, new_only)
            if stop:
                break
        return medias_queued

    def _add_media_to_queue(self, media, condition, media_count, medias_queued, new_only):
        if media.get('__typename') == "GraphSidecar":
            return self._add_sidecars_to_queue(
                media, condition, media_count, medias_queued, new_only)
        elif condition(media):
            media_basename = self._make_filename(media)
            if not os.path.exists(os.path.join(self.directory, media_basename)):
                medias_queued += 1
                self._medias_queue.put(media)
            # stop here if the file already exists and we want only new files
            elif new_only:
                return medias_queued, True
            # stop here if we have as many files queued as wanted
            if media_count is not None and medias_queued >= media_count:
                return medias_queued, True
        return medias_queued, False

    def _add_sidecars_to_queue(self, media, condition, media_count, medias_queued, new_only):
        media = self.get_post_info(media.get('shortcode') or media['code'])
        for index, sidecar in enumerate(media['edge_sidecar_to_children']['edges']):
            sidecar = self._sidecar_to_media(sidecar['node'], media, index)
            medias_queued, stop = self._add_media_to_queue(
                sidecar, condition, media_count, medias_queued, new_only)
            if stop:
                break
        return medias_queued, stop

    def _make_filename(self, media):

        try:
            media['owner'].update(self._OWNER_MAP[media['owner']['id']])
        except KeyError:
            pass

        required_template_keys = copy.copy(self._required_template_keys)
        if media['is_video']:
            required_template_keys.append('video_url')
        else:
            required_template_keys.append('display_src')

        try:
            template_values = {}
            for x in required_template_keys:
                template_values[x] = value = self._TEMPLATE_MAP[x](media)
                if value is None:
                    raise ValueError
        except ValueError:
            media = self.get_post_info(media.get('code') or media['shortcode'])
            template_values = {x:self._TEMPLATE_MAP[x](media) for x in required_template_keys}
        finally:
            self._OWNER_MAP[media['owner']['id']] = media['owner']

        extension = os.path.splitext(os.path.basename(
            media.get('video_url') or media['display_src']
        ).split('?')[0])[1]

        return "".join([self.template.format(**template_values), extension])

    def _join_workers(self, with_pbar=False):
        while any(w.is_alive() for w in self._workers):
            if with_pbar and hasattr(self, '_pbar'):
                with self.dl_count_lock:
                    self._pbar.update(self.dl_count)
        if with_pbar and hasattr(self, '_pbar'):
            with self.dl_count_lock:
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

    @staticmethod
    def _sidecar_to_media(sidecar, media, index):
        for key in ("owner", "location"):
            sidecar.setdefault(key, media[key])

        # try to get a caption if available
        captions = media['edge_media_to_caption']['edges']
        try:
            sidecar['caption'] = captions[index]['node']['text']
        except IndexError:
            if captions:
                sidecar['caption'] = captions[0]['node']['text']

        sidecar['likes'] = media['edge_media_preview_like']
        sidecar['comments'] = media['edge_media_to_comment']
        sidecar['display_src'] = sidecar['display_url']
        sidecar['code'] = sidecar['shortcode']
        sidecar['date'] = media['taken_at_timestamp']
        return sidecar

    def is_logged_in(self):
        """Check if the current instance is logged in.

        Returns:
            `bool`: if the user is logged in or not
        """
        return self.session.cookies._cookies.get(
            "www.instagram.com", {"/":{}})["/"].get("sessionid") is not None
