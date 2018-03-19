#!/usr/bin/env python
# coding: utf-8
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import functools
import hues
import os
import sys
import warnings


console = hues.SimpleConsole(stdout=sys.stderr)


def warn_with_hues(message, category, filename, lineno, file=None, line=None):
    """Use `hues` to log warnings.
    """
    console.warn(message)


def warn_windows(message, category, filename, lineno, file=None, line=None):
    """Use a `hues`-like format to log warnings without color.
    """
    print(("{d.hour}:{d.minute}:{d.second} - WARNING - "
          "{msg}").format(d=datetime.datetime.now(), msg=message), file=sys.stderr)


def wrap_warnings(func):
    """Have the function patch `warnings.showwarning` when it is called.
    """
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        showwarning = warnings.showwarning
        if os.name == 'posix':
            warnings.showwarning = warn_with_hues
        else:
            warnings.showwarning = warn_windows
        try:
            return func(*args, **kwargs)
        finally:
            warnings.showwarning = showwarning
    return new_func
