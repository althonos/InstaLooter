# coding: utf-8
"""Progress bars used to report `InstaLooter.download` progress.

THe module exposes and abstract class that can be derived to implement
your own progress displayer. The default implementation (which uses the
`tqdm` library) is used by the CLI.
"""
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
        self.__lock = None

    def __iter__(self):
        return self

    def __next__(self):
        item = next(self.it)
        self.update()
        return item

    if six.PY2:
        next = __next__

    @abc.abstractmethod
    def update(self):
        return NotImplemented

    @abc.abstractmethod
    def set_maximum(self, maximum):
        return NotImplemented

    def finish(self):
        pass

    def set_lock(self, lock):
        self.__lock = lock

    def get_lock(self):
        if self.__lock is None:
            raise RuntimeError("lock was not initialised")
        return self.__lock


class TqdmProgressBar(tqdm.tqdm, ProgressBar):

    def __init__(self, it, *args, **kwargs):
        kwargs["leave"] = False
        super(TqdmProgressBar, self).__init__(it, *args, **kwargs)
        ProgressBar.__init__(self, it)

    def set_maximum(self, maximum):
        self.total = maximum

    def update(self):
        super(TqdmProgressBar, self).update()

    def finish(self):
        self.close()
