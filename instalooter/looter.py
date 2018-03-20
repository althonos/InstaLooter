# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import abc
import atexit
import itertools
import operator
import os
import random
import sys
import threading
import time
import warnings

import fs
import requests
import six

from fs.base import FS

from . import __author__, __name__ as __appname__, __version__
from .iterators import pages

from .iterators.medias import TimedMediasIterator, MediasIterator
from .pbar import ProgressBar
from .worker import InstaDownloader

from ._utils.libs import length_hint
from ._utils.namegen import NameGenerator
from ._utils.cookies import load_cookies, save_cookies


# mypy annotations
if False:
    from typing import *
    from datetime import datetime
    from queue import Queue
    # type of `timeframe` argument for methods that accept it
    _Timeframe = Tuple[Optional[datetime], Optional[datetime]]


@six.add_metaclass(abc.ABCMeta)
class InstaLooter(object):

    #: The filesystem where cache date is located
    cachefs = fs.open_fs(
        "usercache://{}:{}:{}".format(__appname__, __author__, __version__),
        create=True) # type: FS

    #: The name of the cookie file in the cache filesystem
    _COOKIE_FILE = "cookies.txt"

    @classmethod
    def _login(cls, username, password, session=None):
        # type: (str, str, Optional[requests.Session]) -> None
        """Login with provided credentials.

        Arguments:
            username (`str`): the username to log in with
            password (`str`): the password to log in with

        Note:
            Code taken from LevPasha/instabot.py
        """

        if session is None:
            session = requests.Session()

        homepage = "https://www.instagram.com/"
        data = {'username': username, 'password': password}

        session.headers.update({
            'Origin': homepage,
            'Referer': homepage,
            'X-Instragram-AJAX': '1',
            'X-Requested-With': 'XMLHttpRequest',
        })

        with session.get(homepage) as res:
            session.headers.update({'X-CSRFToken': res.cookies['csrftoken']})
        time.sleep(5 * random.random()) # nosec

        url = "https://www.instagram.com/accounts/login/ajax/"
        with session.post(url, data=data, allow_redirects=True) as res:
            session.headers.update({'X-CSRFToken': res.cookies['csrftoken']})
            if not res.status_code == 200:
                raise SystemError("Login error: check your connection")

        with session.get(url) as res:
            if res.text.find(username) == -1:
                raise ValueError('Login error: check your login data')
            save_cookies(session)

    @classmethod
    def _logout(cls, session=None):
        # type: (Optional[requests.Session]) -> None
        """Log out from current session.

        Note:
            Code taken from LevPasha/instabot.py
        """

        if session is None:
            session = requests.Session()

        try:
            sessionid = next(ck.value
                for ck in session.cookies
                if ck.domain == "www.instagram.com"
                and ck.path == "/" and ck.name == "sessionid")
            url = "https://www.instagram.com/accounts/logout/"
            session.post(url, data={"csrfmiddlewaretoken": sessionid})
        except StopIteration:
            sessionid = None

        if cls.cachefs.exists(cls._COOKIE_FILE):
            cls.cachefs.remove(cls._COOKIE_FILE)

    def __init__(self,
                 add_metadata=False,
                 get_videos=False,
                 videos_only=False,
                 jobs=16,
                 template="{id}",
                 dump_json=False,
                 dump_only=False,
                 extended_dump=False,
                 session=None           # type: Optional[requests.Session]
                 ):
        # type: (...) -> None

        self.add_metadata = add_metadata
        self.get_videos = get_videos or videos_only
        self.videos_only = videos_only
        self.jobs = jobs
        self.namegen = NameGenerator(template)
        self.dump_only = dump_only
        self.dump_json = dump_json or dump_only
        self.extended_dump = extended_dump

        self.session = session or requests.Session()
        atexit.register(self.session.close)
        self.session.cookies = six.moves.http_cookiejar.LWPCookieJar(
            self.cachefs.getsyspath(self._COOKIE_FILE))
        load_cookies(self.session)

    @abc.abstractmethod
    def pages(self):
        # type: () -> Iterable[dict]
        return NotImplemented

    def _medias(self, pages_iterator, timeframe=None):
        # type: (Iterable[dict], Optional[_Timeframe]) -> MediasIterator
        if timeframe is not None:
            return TimedMediasIterator(pages_iterator, timeframe)
        return MediasIterator(pages_iterator)

    def medias(self, timeframe=None):
        # type: (Optional[_Timeframe]) -> MediasIterator
        return self._medias(self.pages(), timeframe)

    def get_post_info(self, code):
        # type: (str) -> dict
        url = "https://www.instagram.com/p/{}/?__a=1".format(code)
        with self.session.get(url) as res:
            return res.json()['graphql']['shortcode_media']

    def download_pictures(self,
                          destination,       # type: Union[str, FS]
                          media_count=None,  # type: Optional[int]
                          timeframe=None,    # type: Optional[_Timeframe]
                          new_only=False,    # type: bool
                          pgpbar_cls=None,   # type: Optional[Type[ProgressBar]]
                          dlpbar_cls=None    # type: Optional[Type[ProgressBar]]
                          ):
        # type: (...) -> int

        return self.download(
            destination,
            condition=lambda media: not media["is_video"],
            media_count=media_count,
            timeframe=timeframe,
            new_only=new_only,
            pgpbar_cls=pgpbar_cls,
            dlpbar_cls=dlpbar_cls,
        )

    def download_videos(self,
                        destination,       # type: Union[str, FS]
                        media_count=None,  # type: Optional[int]
                        timeframe=None,    # type: Optional[_Timeframe]
                        new_only=False,    # type: bool
                        pgpbar_cls=None,   # type: Optional[Type[ProgressBar]]
                        dlpbar_cls=None,   # type: Optional[Type[ProgressBar]]
                        ):
        # type: (...) -> int

        return self.download(
            destination,
            condition=operator.itemgetter("is_video"),
            media_count=media_count,
            timeframe=timeframe,
            new_only=new_only,
            pgpbar_cls=pgpbar_cls,
            dlpbar_cls=dlpbar_cls,
        )

    def download(self,
                 destination,           # type: Union[str, FS]
                 condition=None,        # type: Optional[Callable[[dict], bool]]
                 media_count=None,      # type: Optional[int]
                 timeframe=None,        # type: Optional[_Timeframe]
                 new_only=False,        # type: bool
                 pgpbar_cls=None,       # type: Optional[Type[ProgressBar]]
                 dlpbar_cls=None,       # type: Optional[Type[ProgressBar]]
                 ):
        # type: (...) -> int

        # Open the destination filesystem
        destination, close_destination = self._init_destfs(destination)

        # Create an iterator over the pages with an optional progress bar
        pages_iterator = self.pages()
        pages_iterator = pgpbar = self._init_pbar(pages_iterator, pgpbar_cls)

        # Create an iterator over the medias
        medias_iterator = self._medias(iter(pages_iterator), timeframe)

        # Create the media download bar from a dummy iterator
        dlpbar = self._init_pbar(
            six.moves.range(length_hint(medias_iterator)), dlpbar_cls)

        # Start a group of workers
        workers, queue = self._init_workers(
            dlpbar if dlpbar_cls is not None else None, destination)

        # Make sure exiting the main thread will shutdown workers
        atexit.register(self._shutdown_workers, workers)

        # Queue all medias
        medias_queued = self._fill_media_queue(
            queue, destination, medias_iterator, media_count,
            new_only, condition)

        # Once queuing the medias is fininished, finish the page progress bar
        # and set a new maximum on the download progress bar.
        if pgpbar_cls is not None:
            pgpbar.finish()
        if dlpbar_cls is not None:
            dlpbar.set_maximum(medias_queued)

        # If no medias were queued, issue a warning
        # TODO: refine warning depending on download parameters
        if medias_queued == 0:
            warnings.warn("No medias found.")

        # Add poison pills to the queue and wait for workers to finish
        self._poison_workers(workers, queue)
        self._join_workers(workers, queue)

        # Once downloading is finished, finish the download progress bar
        # and close the destination if needed.
        if dlpbar_cls is not None:
            dlpbar.finish()
        if close_destination:
            destination.close()

        return medias_queued

    def login(self, username, password):
        # type: (str, str) -> None
        self._login(username, password, session=self.session)

    def logout(self):
        # type: () -> None
        self._logout(session=self.session)

    def _init_pbar(self,
                   it,
                   pbar_cls,   # type: Optional[Type[ProgressBar]]
                   ):
        # type: (...) -> Union[ProgressBar, Iterable[Any]]
        if pbar_cls is not None:
            if not issubclass(pbar_cls, ProgressBar):
                raise TypeError("pbar must implement the ProgressBar interface !")
            maximum = length_hint(it)
            it = pbar = pbar_cls(it)
            pbar.set_maximum(maximum)
            pbar.set_lock(threading.RLock())
        return it

    def _init_destfs(self, destination, create=True):
        # type: (Union[str, FS], bool) -> (FS, bool)
        close_destination = False
        if isinstance(destination, six.binary_type):
            destination = destination.decode('utf-8')
        if isinstance(destination, six.text_type):
            destination = fs.open_fs(destination, create=create)
            close_destination = True
        if not isinstance(destination, FS):
            raise TypeError("<destination> must be a FS URL or FS instance.")
        return destination, close_destination

    def _fill_media_queue(self,
                          queue,            # type: six.moves.queue.Queue
                          destination,      # type: FS
                          medias_iterator,  # type: Iterable[Any]
                          media_count=None, # type: Optional[int]
                          new_only=False,   # type: bool
                          condition=None,   # type: Optional[Callable[[dict], bool]]
                          ):
        # type: (...) -> int

        # Create a condition from parameters if needed
        if condition is None:
            if self.videos_only:
                def condition(media): return media['is_video']
            elif not self.get_videos:
                def condition(media): return not media['is_video']
            else:
                def condition(media): return True

        # Queue all media filling the condition
        medias_queued = 0
        for media in six.moves.filter(condition, medias_iterator):

            # Check if the whole post info is required
            if self.namegen.needs_extended(media) or media["__typename"] != "GraphImage":
                media = self.get_post_info(media['shortcode'])

            # Check that sidecar children fit the condition
            if media['__typename'] == "GraphSidecar":
                # Check that each node fits the condition
                for sidecar in media['edge_sidecar_to_children']['edges'][:]:
                    if not condition(sidecar['node']):
                        media['edge_sidecar_to_children']['edges'].remove(sidecar)

                # Check that the nodelist is not depleted
                if not media['edge_sidecar_to_children']['edges']:
                    continue

            # Check that the file does not exist
            # FIXME: not working well with sidecar
            if destination.exists(self.namegen.file(media)):
                if new_only:
                    break

            # Put the medias in the queue
            queue.put(media)
            medias_queued += 1

            if media_count is not None and medias_queued >= media_count:
                break

        return medias_queued

    # WORKERS UTILS

    def _init_workers(self,
                      pbar,         # type: Optional[ProgressBar]
                      destination,  # type: FS
                      ):
        # type: (...) -> Tuple[List[InstaDownloader], Queue]

        workers = []                        # type: List[InstaDownloader]
        queue = six.moves.queue.Queue()     # type: Queue

        for _ in six.moves.range(self.jobs):
            worker = InstaDownloader(
                queue=queue,
                destination=destination,
                namegen=self.namegen,
                add_metadata=self.add_metadata,
                dump_json=self.dump_json,
                dump_only=self.dump_only,
                pbar=pbar,
                session=self.session)
            worker.start()
            workers.append(worker)

        return workers, queue

    def _poison_workers(self, workers, queue):
        # type: (List[InstaDownloader], Queue) -> None
        for worker in workers:
            queue.put(None)

    def _join_workers(self, workers, queue):
        # type: (List[InstaDownloader], Queue) -> None
        if any(w.is_alive() for w in workers):
            for worker in workers:
                worker.join()

    def _shutdown_workers(self, workers):
        # type: (List[InstaDownloader]) -> None
        for worker in workers:
            worker.terminate()



class ProfileLooter(InstaLooter):

    def __init__(self,
                 username,  # type: str
                 **kwargs
                 ):
        # type: (...) -> None
        super(ProfileLooter, self).__init__(**kwargs)
        self._username = username
        self._owner_id = None

    def pages(self):
        if self._owner_id is None:
            it = pages.ProfileIterator.from_username(self._username, self.session)
            self._owner_id = it.owner_id
            return it
        return pages.ProfileIterator(self._owner_id, self.session)



class HashtagLooter(InstaLooter):

    def __init__(self,
                 hashtag,   # type: str
                 **kwargs
                 ):
        # type: (...) -> None
        super(HashtagLooter, self).__init__(**kwargs)
        self._hashtag = hashtag

    def pages(self):
        return pages.HashtagIterator(self._hashtag, self.session)



class PostLooter(InstaLooter):

    def __init__(self,
                 code,      # type: str
                 **kwargs
                 ):
        # type: (...) -> None
        super(PostLooter, self).__init__(**kwargs)
        self.code = code
        self._info = None   # type: Optional[dict]

    @property
    def info(self):
        if self._info is None:
            self._info = self.get_post_info(self.code)
        return self._info

    def pages(self):
        yield {"edge_owner_to_timeline_media": {
            "count": 1,
            "page_info": {
                "has_next_page": False,
                "end_cursor": None,
            },
            "edges": [
                {"node": self.info}
            ],
        }}

    def medias(self, timeframe=None):
        info = self.info
        if timeframe is not None:
            start, end = TimedMediasIterator.get_times(timeframe)
            timestamp = info.get("taken_at_timestamp") or info["media"]
            if not (start >= media_date >= end):
                raise StopIteration
        yield info

    def download(self,
                 destination,       # type: Union[str, FS]
                 condition=None,    # type: Optional[Callable[[dict], bool]]
                 media_count=None,  # type: Optional[int]
                 timeframe=None,    # type: Optional[_Timeframe]
                 new_only=False,    # type: bool
                 pgpbar_cls=None,   # type: Optional[Type[ProgressBar]]
                 dlpbar_cls=None):  # type: Optional[Type[ProgressBar]]
        # type: (...) -> int

        destination, close_destination = self._init_destfs(destination)

        queue = six.moves.queue.Queue()
        medias_queued = self._fill_media_queue(
            queue, destination, iter(self.medias()), media_count,
            new_only, condition)
        queue.put(None)

        worker = InstaDownloader(
            queue=queue,
            destination=destination,
            namegen=self.namegen,
            add_metadata=self.add_metadata,
            dump_json=self.dump_json,
            dump_only=self.dump_only,
            pbar=None,
            session=self.session)
        worker.run()

        return medias_queued
