# coding: utf-8
"""Internal utility classes and functions.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import operator
import os
import pickle
from typing import Any, Dict, Mapping, Optional, Text

import six


class NameGenerator(object):
    """Generator for filenames using a templitertoolsitertoolsitertoolsate.
    """

    @classmethod
    def _get_info(cls, media):
        # type: (Mapping[Text, Any]) -> Mapping[Text, Any]

        info = {
            'id': media['id'],
            'code': media['shortcode'],
            'ownerid': media['owner']['id'],
            'username': media['owner'].get('username'),
            'fullname': media['owner'].get('full_name'),
            'commentscount': media['edge_media_to_comment']['count'],
            'likescount': media['edge_media_preview_like']['count'],
            'width': media.get('dimensions', {}).get('width'),
            'height': media.get('dimensions', {}).get('height'),
        }  # type: Dict[Text, Any]

        timestamp = media.get('date') or media.get('taken_at_timestamp')
        if timestamp is not None:
            dt = datetime.datetime.fromtimestamp(timestamp)
            info['datetime'] = ("{0.year}-{0.month}-{0.day} {0.hour}"
                "h{0.minute}m{0.second}s{0.microsecond}").format(dt)
            info['date'] = datetime.date.fromtimestamp(timestamp)

        return dict(six.moves.filter(
            operator.itemgetter(1), six.iteritems(info)))

    def __init__(self, template="{id}"):
        # type: (Text) -> None
        self.template = template

    def base(self, media):
        # type: (Mapping[Text, Any]) -> Text
        info = self._get_info(media)
        return self.template.format(**info)

    def file(self, media, ext=None):
        # type: (Mapping[Text, Any], Optional[Text]) -> Text
        ext = ext or ("mp4" if media['is_video'] else "jpg")
        return os.path.extsep.join([self.base(media), ext])

    def needs_extended(self, media):
        # type: (Mapping[Text, Any]) -> bool
        try:
            self.base(media)
            return False
        except KeyError:
            return True


def save_cookies(cookiejar, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(cookiejar, f)


def load_cookies(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)
