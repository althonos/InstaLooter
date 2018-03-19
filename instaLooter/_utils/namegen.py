# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import itertools
import operator
import os

import six


class NameGenerator(object):

    # _TEMPLATE_MAP = {
    #     'id': lambda m: m.get('id'),
    #     'code': lambda m: m.get('code') or m.get('shortcode'),
    #     'ownerid': lambda m: m.get('owner', dict()).get('id'),
    #     'username': lambda m: m.get('owner', dict()).get('username'),
    #     'fullname': lambda m: m.get('owner', dict()).get('full_name'),
    #     'datetime': lambda m: ("{0.year}-{0.month}-{0.day} {0.hour}h{0.minute}m{0.second}"
    #         "s{0.microsecond}".format(datetime.datetime.fromtimestamp(m['date'])))
    #         if 'date' in m else None,
    #     'date': lambda m: datetime.date.fromtimestamp(m['date'])
    #         if 'date' in m else None,
    #     'width': lambda m: m.get('dimensions', dict()).get('width'),
    #     'height': lambda m: m.get('dimensions', dict()).get('height'),
    #     'likescount': lambda m: m.get('likes', dict()).get('count'),
    #     'commentscount': lambda m: m.get('comments', dict()).get('count'),
    #     'display_url': lambda m: m.get('display_url'),
    #     'video_url': lambda m: m.get('video_url'),
    # }

    @classmethod
    def _get_info(cls, media):
        info = {
            'id': media['id'],
            'shortcode': media['shortcode'],
            'ownerid': media['owner']['id'],
            'username': media['owner'].get('username'),
            'fullname': media['owner'].get('full_name'),
            'commentscount': media['edge_media_to_comment']['count'],
            'likescount': media['edge_media_preview_like']['count'],
            'width': media.get('dimensions', {}).get('width'),
            'height': media.get('dimensions', {}).get('height'),
        }

        timestamp = media.get('date') or media.get('taken_at_timestamp')
        if timestamp is not None:
            dt = datetime.datetime.fromtimestamp(timestamp)
            info['datetime'] = ("{0.year}-{0.month}-{0.day} {0.hour}"
                "h{0.minute}m{0.second}s{0.microsecond}").format(dt)
            info['date'] = datetime.date.fromtimestamp(timestamp)

        return dict(six.moves.filter(operator.itemgetter(1), six.iteritems(info)))

    def __init__(self, template="{id}"):
        self.template = template

    def base(self, media):
        info = self._get_info(media)
        return self.template.format(**info)

    def file(self, media, ext=None):
        ext = ext or ("mp4" if media['is_video'] else "jpg")
        return os.path.extsep.join([self.base(media), ext])

    def needs_extended(self, media):
        try:
            self.base(media)
            return False
        except KeyError:
            return True
