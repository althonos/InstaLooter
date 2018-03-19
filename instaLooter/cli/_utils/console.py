#!/usr/bin/env python
# coding: utf-8
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import functools
import logging
import warnings

logging.SPAM = 5
logging.NOTICE = 25
logging.SUCCESS = 35


def warn_logging(logger):
    def showwarning(message, category, filename, lineno, file=None, line=None):
        logger.warning(message)
    return showwarning


def wrap_warnings(logger):
    """Have the function patch `warnings.showwarning` with the given logger.

    Arguments:
        logger: a `~logging.Logger` instance.

    Returns:
        `function`: a decorator function.
    """
    def decorator(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            showwarning = warnings.showwarning
            warnings.showwarning = warn_logging(logger)
            try:
                return func(*args, **kwargs)
            finally:
                warnings.showwarning = showwarning
        return new_func
    return decorator
