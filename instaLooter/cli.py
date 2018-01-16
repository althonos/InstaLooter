#!/usr/bin/env python
# coding: utf-8
"""
instaLooter - Another API-less Instagram pictures and videos downloader

Usage:
    instaLooter (login | logout)
    instaLooter batch <batch_file>
    instaLooter <profile> [<directory>] [options]
    instaLooter (hashtag <hashtag> | post <post_token>) <directory> [options]
    instaLooter (-h | --help | --version | --usage)

Arguments:
    <profile>                    The username of the profile to download
                                 videos and pictures from.
    <hashtag>                    A hashtag to download pictures and videos
                                 from.
    <post_token>                 Either the url or the code of a single post
                                 to download the picture or video from.
    <directory>                  The directory in which to download files.
    <batch_file>                 The path to the batch file containing batch
                                 download instructions (see the online
                                 documentation).

Options - Credentials:
    -u USER, --username USER     The username to connect to Instagram with.
    -p PASS, --password PASS     The password to connect to Instagram with
                                 (will be asked in the shell if the `--username`
                                  option was given without the corresponding
                                  `--password`).

Options - Files:
    -n NUM, --num-to-dl NUM      Maximum number of new files to download
    -j JOBS, --jobs JOBS         Number of parallel threads to use to
                                 download files. [default: 16]
    -T TMPL, --template TMPL     A filename template to use to write the
                                 files (see *Template*). [default: {id}]
    -v, --get-videos             Get videos as well as photos.
    -V, --videos-only            Get videos only.
    -N, --new                    Only look for files newer than the ones
                                 in the destination directory (faster).
    -t TIME, --time TIME         The time limit within which to download
                                 pictures and video (see *Time*).

Options - Metadata:
    -m, --add-metadata           Add date and caption metadata to downloaded
                                 pictures (requires PIL/Pillow and piexif).
    -d, --dump-json              Save metadata to a JSON file next to
                                 downloaded videos/pictures.
    -D, --dump-only              Save only the metadata and no video / picture.
    -e, --extended-dump          Always dump the maximum amount of extracted
                                 information, at the cost of more time.

Options - Miscellaneous:
    -q, --quiet                  Do not produce any output.
    -h, --help                   Display this message and quit.
    --version                    Show program version and quit.
    --traceback                  Print error traceback if any (debug).
    -W WARNINGCTL                Change warning behaviour (same as python -W).
                                 [default: default]
                                 
Options - Tor:
    --socks_port PORT            SOCKS port for tor instance.
    --control_port PORT          Control port for tor instance. Can be ommited,
                                 thus control port will be `socks_port + 1`.
    --change_ip_after N          Number of requests after which tor instance
                                 will change IP adress. [default: 10]

Template:
    The default filename of the pictures and videos on Instagram doesn't show
    anything about the file you just downloaded. But using the -T argument
    allows you to give instaLooter a filename template, using the following
    format with brackets-enclosed ({}) variable names among:
    - ``id``*² and ``code``² of the instagram id of the media
    - ``ownerid``*, ``username`` and ``fullname`` of the owner
    - ``datetime``*: the date and time of the post (YYYY-MM-DD hh:mm:ss)
    - ``date``*: the date of the post (YYYY-MM-DD)
    - ``width``* and ``height``*
    - ``likescount``* and ``commentscount``*

    ²: use at least one of these to make sure the generated file name
    is unique (``datetime`` is not unique anymore since multiple-image-posts).

    *: use these only to quicken download, since fetching the others may take
    a tad longer (in particular in hashtag download mode).

    You are however to make sure that the generated filename is unique, so you
    should use at least id, code or datetime somewhere.
    Examples of acceptable values:
        - {username}.{datetime}.{code}
        - {username}-{likescount}-{width}x{height}.{id}

Time:
    The --time parameter can be given either a combination of start and stop
    date in ISO format (e.g. 2016-12-21:2016-12-18, 2015-03-07:, :2016-08-02)
    or a special value among: "thisday", "thisweek", "thismonth", "thisyear".

    Edges are included in the time frame, so if using the following value:
    `--time 2016-05-10:2016-04-03`, then all medias will be downloaded
    including the ones posted the 10th of May 2016 and the 3rd of April 2016.

See more at http://instalooter.readthedocs.io/en/latest/usage.html

"""
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
import getpass
import warnings
import traceback

import six
import hues
import docopt

from . import __version__
from .core import InstaLooter
from .batch import BatchRunner
from .utils import get_times_from_cli, console, wrap_warnings

WARNING_ACTIONS = {
    'error', 'ignore', 'always', 'default', 'module', 'once'
}


def usage():
    return next(s for s in __doc__.split("\n\n") if s.startswith("Usage"))


def login(looter, args):
    if args['--username']:
        username = args['--username']
        if not looter.is_logged_in():
            password = args['--password'] or getpass.getpass()
            looter.login(username, password)
            if not args['--quiet']:
                hues.success('Logged in.')
        elif not args['--quiet']:
            hues.success("Already logged in.")


@wrap_warnings
def main(argv=None):
    """Run from the command line interface.
    """
    argv = argv or sys.argv[1:]

    try:
        args = docopt.docopt(__doc__, argv,
                             version='instaLooter {}'.format(__version__))
    except docopt.DocoptExit as de:
        print(de)
        return 1

    argv_positional = [param for param in argv if not param.startswith("-")]
    if argv_positional[0] in ("post", "hashtag") and len(argv_positional) < 3:
        print(usage())
        return 1

    if args['logout']:
        if not os.path.exists(InstaLooter.COOKIE_FILE):
            hues.error('Cookie file not found.')
            return 1
        InstaLooter().logout()
        hues.success('Logged out.')
        return 0

    elif args['login']:
        try:
            args['--username'] = six.moves.input('Username: ')
            login(InstaLooter(), args)
            return 0
        except ValueError as ve:
            console.error(ve)
            if args["--traceback"]:
               traceback.print_exc()
            return 1

    if args['-W'] not in WARNING_ACTIONS:
        print("Unknown warning action: {}".format(args['-W']))
        print("   available action: {}".format(', '.join(WARNING_ACTIONS)))
        return 1

    if args['batch']:
        with open(args['<batch_file>']) as batch_file:
            batch_runner = BatchRunner(batch_file)
        batch_runner.runAll()
        return 0

    with warnings.catch_warnings():
        warnings.simplefilter(args['-W'])

        # if args['<hashtag>'] and not args['--credentials']:
        #    warnings.warn("#hashtag downloading requires an Instagram account.")
        #    return 1

        if args['<post_token>'] is not None:
            args['--get-videos'] = True

        if args['--socks_port'] is not None:
            args['--socks_port'] = int(args['--socks_port'])

        if args['--control_port'] is not None:
            args['--control_port'] = int(args['--control_port'])

        if args['--change_ip_after'] is not None:
            args['--change_ip_after'] = int(args['--change_ip_after'])

        looter = InstaLooter(
            directory=os.path.expanduser(args.get('<directory>') or os.getcwd()),
            profile=args['<profile>'],hashtag=args['<hashtag>'],
            add_metadata=args['--add-metadata'],
            get_videos=args['--get-videos'],
            videos_only=args['--videos-only'], jobs=int(args['--jobs']),
            template=args['--template'],
            dump_json=args['--dump-json'],
            dump_only=args['--dump-only'],
            extended_dump=args['--extended-dump'],
            socks_port=args['--socks_port'],
            control_port=args['--control_port'],
            change_ip_after=args['--change_ip_after'],
        )

        try:
            login(looter, args)
            if args['--time']:
                timeframe = get_times_from_cli(args['--time'])
            else:
                timeframe = None
        except ValueError as ve:
            console.error(ve)
            if args["--traceback"]:
               traceback.print_exc()
            return 1

        try:
            post_token = args['<post_token>']
            if post_token is None:
                media_count = int(args['--num-to-dl']) if args['--num-to-dl'] else None
                looter.download(
                    media_count=media_count,
                    with_pbar=not args['--quiet'],
                    timeframe=timeframe,
                    new_only=args['--new'],
                )
            else:
                if 'insta' in post_token:
                    post_token = looter._extract_code_from_url(post_token)
                looter.download_post(post_token)

        except Exception as e:
            console.error(e)
            if args["--traceback"]:
               traceback.print_exc()
            return 1

        except KeyboardInterrupt:
            return 1

        else:
            return 0


if __name__ == "__main__":
    main()
