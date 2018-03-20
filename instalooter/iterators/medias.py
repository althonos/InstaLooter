# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import collections
import datetime
import functools

import requests
import six


__all__ = [
    "MediasIterator",
    "TimedMediasIterator",
]


class MediasIterator(collections.Iterator):

    def __init__(self, page_iterator):
        self._it = page_iterator
        self._seen = set()
        self._edges = []
        self._finished = False
        self._total = None
        self._done = 0
        self._tmp = None

    def __iter__(self):
        return self

    def _next_page(self):
        data = next(self._it)
        section = next(s for s in six.iterkeys(data) if s.endswith('_media'))
        return data[section]

    def __next__(self):

        if self._finished:
            raise StopIteration

        if not self._edges:
            page = self._next_page()
            self._total = page['count']
            self._edges.extend(page['edges'])

        media = self._edges.pop(0)
        self._done += 1

        if media['node']['id'] in self._seen:
            self._finished = True

        self._seen.add(media['node']['id'])
        return media['node']

    def __length_hint__(self):
        if self._total is None:
            try:
                page = self._next_page()
                self._total = page['count']
                self._edges.extend(page['edges'])
            except StopIteration:
                self._total = 0
        return self._total - self._done

    if six.PY2:
        next = __next__


class TimedMediasIterator(MediasIterator):

    @staticmethod
    def get_times(timeframe):
        if timeframe is None:
            timeframe = (None, None)
        try:
            start_time = timeframe[0] or datetime.date.today()
            end_time = timeframe[1] or datetime.date.fromtimestamp(0)
        except (IndexError, AttributeError):
            raise TypeError("'timeframe' must be a couple of dates!")
        return start_time, end_time

    def __init__(self, page_iterator, timeframe=None):
        super(TimedMediasIterator, self).__init__(page_iterator)
        self.start_time, self.end_time = self.get_times(timeframe)

    def __next__(self):
        while True:
            media = super(TimedMediasIterator, self).__next__()
            timestamp = media.get('taken_at_timestamp') or media['date']
            media_date = datetime.date.fromtimestamp(timestamp)

            if self.start_time >= media_date >= self.end_time:
                return media
            elif media_date < self.end_time:
                self._finished = True
                raise StopIteration

    if six.PY2:
        next = __next__
