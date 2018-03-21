# coding: utf-8
"""Progress bars used to report `InstaLooter.download` progress.

The module exposes and abstract class that can be derived to implement
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
    """An abstract progess bar used to report interal progress.
    """

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
        """Update the progress bar by one step.
        """
        return NotImplemented

    @abc.abstractmethod
    def set_maximum(self, maximum):
        """Set the maximum number of steps of the operation.
        """
        return NotImplemented

    def finish(self):
        """Notify the progress bar the operation is finished.
        """
        pass

    def set_lock(self, lock):
        """Set a lock to be used by parallel workers.
        """
        self.__lock = lock

    def get_lock(self):
        """Obtain the progress bar lock.
        """
        if self.__lock is None:
            raise RuntimeError("lock was not initialised")
        return self.__lock


class TqdmProgressBar(tqdm.tqdm, ProgressBar):
    """A progress bar using the `tqdm` library.
    """

    def __init__(self, it, *args, **kwargs):
        kwargs["leave"] = False
        super(TqdmProgressBar, self).__init__(it, *args, **kwargs)
        ProgressBar.__init__(self, it)

    def set_maximum(self, maximum):
        self.total = maximum

    def update(self):
        """Update the progress bar by one step.
        """
        super(TqdmProgressBar, self).update()

    def finish(self):
        self.close()
