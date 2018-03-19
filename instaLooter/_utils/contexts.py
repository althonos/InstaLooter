# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import contextlib


@contextlib.contextmanager
def on_exception(callback, *args, **kwargs):
    try:
        yield
    except BaseException:
        callback(*args, **kwargs)
        raise
