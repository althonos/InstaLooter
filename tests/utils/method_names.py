# coding: utf-8
from __future__ import absolute_import

def signature(func, param_num, params):
    args = ','.join("{!r}".format(a) for a in params.args)
    kwargs = ','.join("{}={!r}".format(k, v) for k,v in params.kwargs.items())
    if args and kwargs:
        return "{}({},{})".format(func.__name__, args, kwargs)
    else:
        return "{}({})".format(func.__name__, args or kwargs)

def firstparam(func, param_num, params):
    return "{}({!r})".format(func.__name__, params.args[0])

def num(func, param_num, params):
    return "{}_{}".format(func.__name__, param_num)
