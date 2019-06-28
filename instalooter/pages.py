# coding: utf-8
"""Iterators over Instagram media pages.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import abc
import hashlib
import itertools
import math
import time
import typing

import six
from requests import Session

from ._impl import json
from ._utils import get_shared_data

if typing.TYPE_CHECKING:
    from typing import Any, Dict, Iterator, Iterable, Optional, Text


__all__ = [
    "PageIterator",
    "HashtagIterator",
    "ProfileIterator",
]


@six.add_metaclass(abc.ABCMeta)
class PageIterator(typing.Iterator[typing.Dict[typing.Text, typing.Any]]):
    """An abstract Instagram page iterator.
    """

    PAGE_SIZE = 50
    INTERVAL = 2

    _BASE_URL = "https://www.instagram.com/graphql/query/"
    _section_generic = NotImplemented    # type: Text
    _section_media = NotImplemented      # type: Text

    def __init__(self, session, rhx):
        # type: (Session) -> None
        self._finished = False
        self._cursor = None     # type: Optional[Text]
        self._current_page = 0
        self._data_it = iter(self._page_loader(session, rhx))

    @abc.abstractmethod
    def _getparams(self, cursor):
        # type: (Optional[Text]) -> Text
        return NotImplemented

    def _page_loader(self, session, rhx):
        # type: (Session) -> Iterable[Dict[Text, Dict[Text, Any]]]
        while True:
            # Cache cursor for later
            cursor = self._cursor
            # Query data
            try:
                # Prepare the query
                params = self._getparams(cursor)
                json_params = json.dumps(params, separators=(',', ':'))
                magic = "{}:{}".format(rhx, json_params)
                session.headers['x-instagram-gis'] = hashlib.md5(magic.encode('utf-8')).hexdigest()
                url = self._URL.format(json_params)
                # Query the server for data
                with session.get(url) as res:
                    self._last_page = data = res.json()
                # Yield that same data until cursor is updated
                while self._cursor == cursor:
                    yield data['data']
            except KeyError as e:
                if data.get('message') == 'rate limited':
                    raise RuntimeError("Query rate exceeded (wait before next run)")
                time.sleep(10)
            # Sleep before next query
            time.sleep(self.INTERVAL)

    def __length_hint__(self):
        # type: () -> int
        try:
            data = next(self._data_it)
            c = data[self._section_generic][self._section_media]['count']
            total = int(math.ceil(c / self.PAGE_SIZE))
        except (StopIteration, TypeError):
            total = 0
        return total - self._current_page

    def __iter__(self):
        return self

    def __next__(self):

        if self._finished:
            raise StopIteration

        data = next(self._data_it)

        try:
            media_info = data[self._section_generic][self._section_media]
        except (TypeError, KeyError):
            self._finished = True
            raise StopIteration

        if not media_info['page_info']['has_next_page']:
            self._finished = True
        elif not media_info['edges']:
            self._finished = True
            raise StopIteration
        else:
            self._cursor = media_info['page_info']['end_cursor']
            self._current_page += 1

        return data[self._section_generic]

    if six.PY2:
        next = __next__


class HashtagIterator(PageIterator):
    """An iterator over the pages refering to a specific hashtag.
    """

    _QUERY_ID = "17882293912014529"
    _URL = "{}?query_id={}&variables={{}}".format(PageIterator._BASE_URL, _QUERY_ID)
    _section_generic = "hashtag"
    _section_media = "edge_hashtag_to_media"

    def __init__(self, hashtag, session, rhx):
        super(HashtagIterator, self).__init__(session, rhx)
        self.hashtag = hashtag

    def _getparams(self, cursor):
        return {
            "tag_name": self.hashtag,
            "first": self.PAGE_SIZE,
            "after": cursor
        }

    def __next__(self):
        item = super(HashtagIterator, self).__next__()
        for media in item[self._section_media].get("edges", []):
            media["node"].setdefault(
                "__typename",
                "GraphVideo" if media["node"].get("is_video", False) else "GraphImage"
            )
        return item

    if six.PY2:
        next = __next__


class ProfileIterator(PageIterator):
    """An iterator over the pages of a user profile.
    """

    _QUERY_HASH = "42323d64886122307be10013ad2dcc44"
    #_QUERY_HASH = "472f257a40c653c64c666ce877d59d2b"
    _URL = "{}?query_hash={}&variables={{}}".format(PageIterator._BASE_URL, _QUERY_HASH)
    _section_generic = "user"
    _section_media = "edge_owner_to_timeline_media"

    @classmethod
    def _user_data(cls, username, session):
        url = "https://www.instagram.com/{}/".format(username)
        try:
            with session.get(url) as res:
                return get_shared_data(res.text)
        except (ValueError, AttributeError):
            raise ValueError("user not found: '{}'".format(username))

    @classmethod
    def from_username(cls, username, session):
        user_data = cls._user_data(username, session)
        if 'ProfilePage' not in user_data['entry_data']:
            raise ValueError("user not found: '{}'".format(username))
        data = user_data['entry_data']['ProfilePage'][0]['graphql']['user']
        if data['is_private'] and not data['followed_by_viewer']:
            con_id = next((c.value for c in session.cookies if c.name == "ds_user_id"), None)
            if con_id != data['id']:
                raise RuntimeError("user '{}' is private".format(username))
        return cls(data['id'], session, user_data.get('rhx_gis', ''))

    def __init__(self, owner_id, session, rhx):
        super(ProfileIterator, self).__init__(session, rhx)
        self.owner_id = owner_id

    def _getparams(self, cursor):
        return {
            "id": self.owner_id,
            "first": self.PAGE_SIZE,
            "after": cursor,
        }
