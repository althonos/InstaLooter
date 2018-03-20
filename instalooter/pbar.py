# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import abc
import threading

import six
import tqdm


@six.add_metaclass(abc.ABCMeta)
class ProgressBar(object):

    def __init__(self, it, *args, **kwargs):
        self.it = it

    def __iter__(self):
        return self

    def __next__(self):
        self.update()
        return next(self.it)

    if six.PY2:
        next = __next__

    @abc.abstractmethod
    def update(self):
        return NotImplemented

    @abc.abstractmethod
    def set_maximum(self, maximum):
        return NotImplemented

    def close(self):
        pass

    def set_lock(self, lock):
        self._lock = lock

    def lock(self):
        try:
            return self._lock
        except AttributeError:
            raise RuntimeError("lock was not initialised")


class TqdmProgressBar(tqdm.tqdm, ProgressBar):

    def __init__(self, it, *args, **kwargs):
        kwargs["leave"] = False
        super(TqdmProgressBar, self).__init__(it, *args, **kwargs)

    def set_maximum(self, maximum):
        self.total = maximum

    def update(self):
        super(TqdmProgressBar, self).update()

    def finish(self):
        self.close()
