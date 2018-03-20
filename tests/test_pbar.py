# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import threading
import unittest
import warnings

import six

from instalooter.pbar import ProgressBar, TqdmProgressBar



class TestProgressBar(unittest.TestCase):

    def test_derived_progress_bar(self):

        class MyProgressBar(ProgressBar):
            _test = {"update": 0, "max": None}
            def update(self):
                self._test['update'] += 1
            def set_maximum(self, maximum):
                self._test['max'] = maximum

        pb = MyProgressBar(iter(range(10)))
        self.assertEqual(pb._test['update'], 0)
        self.assertIs(pb._test['max'], None)

        self.assertEqual(next(pb), 0)
        self.assertEqual(pb._test['update'], 1)

        pb.set_maximum(10)
        self.assertEqual(pb._test['max'], 10)

        self.assertEqual(list(pb), list(range(1, 10)))
        self.assertRaises(StopIteration, next, pb)
        self.assertEqual(pb._test['update'], 10)
        pb.finish()

        self.assertRaises(RuntimeError, pb.get_lock)
        lock = threading.RLock()
        pb.set_lock(lock)
        self.assertIs(pb.get_lock(), lock)

    def test_tqdm_progress_bar(self):

        fh = six.moves.StringIO()
        pb = TqdmProgressBar(iter(range(10)), file=fh)

        self.assertEqual(pb.n, 0)
        self.assertIs(pb.total, None)

        self.assertEqual(next(pb), 0)
        self.assertEqual(pb.n, 1)
        self.assertIs(pb.total, None)

        pb.set_maximum(10)
        self.assertEqual(pb.total, 10)

        self.assertEqual(list(pb), list(range(1, 10)))
        self.assertRaises(StopIteration, next, pb)
        self.assertEqual(pb.n, 10)
        pb.finish()

        lock = threading.RLock()
        pb.set_lock(lock)
        self.assertIs(pb.get_lock(), lock)


def setUpModule():
   warnings.simplefilter('ignore')


def tearDownModule():
   warnings.simplefilter(warnings.defaultaction)
