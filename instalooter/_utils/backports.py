# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals


def length_hint(obj, default=0):
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
