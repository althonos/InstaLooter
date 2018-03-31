# coding: utf-8
from __future__ import absolute_import

import threading

from ..worker import InstaDownloader


def threads_force_join():
    for t in threading.enumerate():
        if isinstance(t, InstaDownloader):
            t.terminate()
            t.join()


def threads_count():
    return sum(isinstance(t, InstaDownloader) for t in threading.enumerate())
