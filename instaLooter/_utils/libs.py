# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

try:
    import ujson as json
except ImportError:
    import json

try:
    import PIL.Image
    import piexif
except ImportError:
    PIL = None
    piexif = None

try:
    from operator import length_hint
except ImportError:
    from .backports import length_hint
