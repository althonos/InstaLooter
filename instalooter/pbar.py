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
import typing

import six
import tqdm


_T = typing.TypeVar('_T')
_L = typing.TypeVar('_L', )


@six.add_metaclass(abc.ABCMeta)
class ProgressBar(typing.Iterator[_T]):
    """An abstract progess bar used to report interal progress.
    """

    def __init__(self, it, *args, **kwargs):
        self.it = it
        self.__lock = None  # type: typing.Union[threading.Lock, threading.RLock, None]

    def __iter__(self):
        # type: () -> ProgressBar[_T]
        return self

    def __next__(self):
        # type: () -> _T
        item = next(self.it)
        self.update()
        return item

    if six.PY2:
        next = __next__

    @abc.abstractmethod
    def update(self):
        # type: () -> None
        """Update the progress bar by one step.
        """
        return NotImplemented

    @abc.abstractmethod
    def set_maximum(self, maximum):
        # type: (int) -> None
        """Set the maximum number of steps of the operation.
        """
        return NotImplemented

    def finish(self):
        # type: () -> None
        """Notify the progress bar the operation is finished.
        """
        pass

    def set_lock(self, lock):
        # type: (typing.Union[threading.Lock, threading.RLock]) -> None
        """Set a lock to be used by parallel workers.
        """
        self.__lock = lock

    def get_lock(self):
        # type: () -> typing.Union[threading.Lock, threading.RLock]
        """Obtain the progress bar lock.
        """
        if self.__lock is None:
            raise RuntimeError("lock was not initialised")
        return self.__lock


class TqdmProgressBar(tqdm.tqdm, ProgressBar):
    """A progress bar using the `tqdm` library.
    """

    def __init__(self, it, *args, **kwargs):  # noqa: D102, D107
        kwargs["leave"] = False
        super(TqdmProgressBar, self).__init__(it, *args, **kwargs)
        ProgressBar.__init__(self, it)

    def set_maximum(self, maximum):  # noqa: D102
        self.total = maximum

    def update(self):
        """Update the progress bar by one step.
        """
        super(TqdmProgressBar, self).update()

    def finish(self):  # noqa: D102
        self.close()
