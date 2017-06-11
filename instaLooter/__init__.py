#!/usr/bin/env python
# coding: utf-8

from __future__ import (
    absolute_import,
    unicode_literals,
)


__author__ = "althonos"
__author_email__ = "martin.larralde@ens-cachan.fr"
__version__ = "0.10.2"


try:
    from .cli import main
    from .core import InstaLooter
    from . import urlgen
except ImportError:
    pass
