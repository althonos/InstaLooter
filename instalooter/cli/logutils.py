#!/usr/bin/env python
# coding: utf-8
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import functools
import logging
import warnings
import typing

if typing.TYPE_CHECKING:
    from typing import Callable


def warn_logging(logger):
    # type: (logging.Logger) -> Callable
    """Create a `showwarning` function that uses the given logger.

    Arguments:
        logger (~logging.Logger): the logger to use.

    Returns:
        function: a function that can be used as the `warnings.showwarning`
            callback.

    """
    def showwarning(message, category, filename, lineno, file=None, line=None):
        logger.warning(message)
    return showwarning


def wrap_warnings(logger):
    """Have the function patch `warnings.showwarning` with the given logger.

    Arguments:
        logger (~logging.logger): the logger to wrap warnings with when
            the decorated function is called.

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
