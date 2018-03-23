# coding: utf-8
"""Backports and alternative library implementations.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import typing

try:
    import simplejson as json
except ImportError:
    import json  # type: ignore

try:
    import PIL.Image
    import piexif
except ImportError:
    PIL = None
    piexif = None

try:
    from operator import length_hint
except ImportError:
    def length_hint(obj, default=0):
        # type: (typing.Any, int) -> int
        """Return an estimate of the number of items in obj.

        This is useful for presizing containers when building from an
        iterable.

        If the object supports len(), the result will be
        exact. Otherwise, it may over- or under-estimate by an
        arbitrary amount. The result will be an integer >= 0.

        See Also:
            `PEP 424 <https://www.python.org/dev/peps/pep-0424/>`_

        """
        try:
            return len(obj)
        except TypeError:
            try:
                get_hint = type(obj).__length_hint__
            except AttributeError:
                return default
            try:
                hint = get_hint(obj)
            except TypeError:
                return default
            if hint is NotImplemented:
                return default
            if not isinstance(hint, int):
                raise TypeError("Length hint must be an integer, not %r" %
                                type(hint))
            if hint < 0:
                raise ValueError("__length_hint__() should return >= 0")
            return hint


__all__ = ["PIL", "piexif", "json", "length_hint"]
