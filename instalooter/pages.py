# coding: utf-8
"""Iterators over Instagram media pages.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import abc
import collections
import functools
import json
import math
import time

import requests
import six


__all__ = [
    "PageIterator",
    "HashtagIterator",
    "ProfileIterator",
]


@six.add_metaclass(abc.ABCMeta)
class PageIterator(collections.Iterator):

    URL_QUERY = "https://www.instagram.com/graphql/query/"
    PAGE_SIZE = 200
    INTERVAL = 0.5

    section_generic = NotImplemented
    section_media = NotImplemented

    def __init__(self, session=None):
        self._session = session or requests.Session()
        self._finished = False
        self._cursor = None
        self._current_page = 0
        self._data_it = iter(self._page_loader(self._session))
        self._total = None
        self._done = 0

    def _page_loader(self, session):
        while True:
            try:
                # time.sleep(self.INTERVAL)
                with session.get(self._geturl(self._cursor)) as res:
                    data = res.json()

                try:
                    c = data['data'][self.section_generic][self.section_media]['count']
                    self._total = math.ceil(c / self.PAGE_SIZE)
                except (KeyError, TypeError):
                    self._total = 0

                yield data['data']
            except KeyError as e:
                time.sleep(10)

    def __length_hint__(self):
        if self._total is None:
            try:
                data = next(self._data_it, None)
                c = data[self.section_generic][self.section_media]['count']
                self._total = int(math.ceil(c / self.PAGE_SIZE))
            except TypeError:
                self._total = 0
        return self._total - self._done

    def __iter__(self):
        return self

    def __next__(self):

        if self._finished:
            raise StopIteration

        data = next(self._data_it)

        try:
            media_info = data[self.section_generic][self.section_media]
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

        return data[self.section_generic]

    if six.PY2:
        next = __next__


class HashtagIterator(PageIterator):

    QUERY_ID = "17882293912014529"
    section_generic = "hashtag"
    section_media = "edge_hashtag_to_media"

    def __init__(self, hashtag, session=None):
        super(HashtagIterator, self).__init__(session)
        self.hashtag = hashtag

    def _geturl(self, cursor):
        return "{base}?query_id={id}&variables={vars}".format(
            base=self.URL_QUERY,
            id=self.QUERY_ID,
            vars=json.dumps({
                "tag_name": self.hashtag,
                "first": self.PAGE_SIZE,
                "after": cursor
            })
        )


class ProfileIterator(PageIterator):

    QUERY_HASH = "472f257a40c653c64c666ce877d59d2b"
    section_generic = "user"
    section_media = "edge_owner_to_timeline_media"

    @classmethod
    def from_username(cls, username, session=None):
        session = session or requests.Session()
        url = "https://www.instagram.com/{}/?__a=1".format(username)
        try:
            with session.get(url) as res:
                data = res.json()
        except ValueError:
            raise ValueError("account not found: {}".format(username))
        else:
            return cls(data['graphql']['user']['id'], session)

    def __init__(self, owner_id, session=None):
        super(ProfileIterator, self).__init__(session)
        self.owner_id = owner_id

    def _geturl(self, cursor):
        return "{base}?query_hash={hash}&variables={vars}".format(
            base=self.URL_QUERY,
            hash=self.QUERY_HASH,
            vars=json.dumps({
                "id": self.owner_id,
                "first": self.PAGE_SIZE,
                "after": cursor,
            })
        )
