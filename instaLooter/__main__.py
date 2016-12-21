#!/usr/bin/env python
# coding: utf-8
"""
instaLooter - Another API-less Instagram pictures and videos downloader

Usage:
    instaLooter <profile> [<directory>] [options]
    instaLooter hashtag <hashtag> [<directory>] [options]
    instaLooter (-h | --help | --version)

Options:
    -n NUM, --num-to-dl NUM      Maximum number of new files to download
    -j JOBS, --jobs JOBS         Number of parallel threads to use to
                                 download files [default: 16]
    -v, --get-videos             Get videos as well as photos
    -m, --add-metadata           Add date and caption metadata to downloaded
                                 pictures (requires PIL/Pillow and piexif)
    -q, --quiet                  Do not produce any output
    -t TIME, --time TIME         The time limit within which to download
                                 pictures and video (see *Time* section)
    -h, --help                   Display this message and quit
    -c CRED, --credentials CRED  Credentials to login to Instagram with if
                                 needed [format: login[:password]]
    --version                    Show program version and quit

Time:
    The --time parameter can be given either a combination of start and stop
    date in ISO format (e.g. 2016-12-21:2016-12-18, 2015-03-07:, :2016-08-02)
    or a special value among: "thisday", "thisweek", "thismonth", "thisyear".

    Edges are included in the time frame, so if using the following value:
    `--time 2016-05-10:2016-04-03`, then all medias will be downloaded
    including the ones posted the 10th of May 2016 and the 3rd of April 2016.
"""
from __future__ import (
    absolute_import,
    unicode_literals,
)

import docopt
import os
import sys
import getpass

from . import __version__, __author__, __author_email__
from .core import InstaLooter
from .utils import get_times_from_cli


def main(argv=sys.argv[1:]):
    """Run from the command line interface.
    """
    args = docopt.docopt(__doc__, argv, version='instaLooter {}'.format(__version__))

    looter = InstaLooter(
        directory=os.path.expanduser(args.get('<directory>', os.getcwd())),
        profile=args['<profile>'],hashtag=args['<hashtag>'],
        add_metadata=args['--add-metadata'], get_videos=args['--get-videos'],
        jobs=int(args['--jobs']))

    if args['--credentials']:
        credentials = args['--credentials'].split(':', 1)
        login = credentials[0]
        password = credentials[1] if len(credentials) > 1 else getpass.getpass()
        looter.login(login, password)

    if args['--time']:
        try:
            timeframe = get_times_from_cli(args['--time'])
        except ValueError as ve:
            print(str(ve))
            sys.exit(1)
    else:
        timeframe = None

    try:
        looter.download(
            media_count=int(args['--num-to-dl']) if args['--num-to-dl'] else None,
            with_pbar=not args['--quiet'], timeframe=timeframe,
        )
    except KeyboardInterrupt:
        looter.__del__()


if __name__ == "__main__":
    main()
