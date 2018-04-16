# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import json

import fs.path
import instalooter.looters


_test_dir = os.path.abspath(os.path.join(__file__, ".."))
_url = "tar://{}/ig_mock.tar.gz".format(_test_dir)


def get_mock_fs():
    return fs.open_fs(_url)


class MockPages(object):

    def __init__(self, profile):
        self.profile = profile

    def __call__(self):
        with get_mock_fs() as mockfs:
            with mockfs.open("pages/{}".format(self.profile)) as f:
                return iter(json.load(f))


if __name__ == "__main__":

    with fs.open_fs(_test_dir) as test_fs:
        if test_fs.exists(fs.path.basename(_url)):
            test_fs.remove(fs.path.basename(_url))

    with fs.open_fs(_url, create=True) as mockfs:
        mockfs.makedir("pages", recreate=True)
        nintendo = instalooter.looters.ProfileLooter("nintendo")
        with mockfs.open("pages/nintendo", "w") as f:
            json.dump(list(nintendo.pages()), f)

        fluoxetine = instalooter.looters.HashtagLooter("fluoxetine")
        with mockfs.open("pages/fluoxetine", "w") as f:
            pages_it = fluoxetine.pages_it
            json.dump([next(pages_it) for _ in range(3)], f)
