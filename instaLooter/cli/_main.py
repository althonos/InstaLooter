# coding: utf-8
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import functools
import logging
import getpass
import os
import sys
import traceback
import warnings

import coloredlogs
import docopt
import fs
import six

from .. import __version__
from ..looter import HashtagLooter, ProfileLooter, PostLooter
from ..pbar import TqdmProgressBar
# from ..batch import BatchRunner

from . import __name__ as __parent__
from ._utils.constants import HELP, USAGE, WARNING_ACTIONS
from ._utils.console import wrap_warnings
from ._utils.time import get_times_from_cli


__all__ = ["main"]


logger = logging.getLogger(__parent__)


@wrap_warnings(logger)
def main(argv=None, stream=None):
    """Run from the command line interface.

    Arguments:
        argv (list): The positional arguments to read. Defaults to
            `sys.argv` to use CLI arguments.
        stream (file handle): A file where to write error messages.
            Leave to `None` to use the `StandardErrorHandler` for
            log, and `sys.stderr` for error messages.
    """

    _print = functools.partial(print, file=stream or sys.stderr)

    try:
        args = docopt.docopt(
            HELP, argv, version='instaLooter {}'.format(__version__))
    except docopt.DocoptExit as de:
        _print(de)
        return 1

    if args['--usage']:
        _print(USAGE, file=sys.stderr)
        return 0

    level = "100" if args['--quiet'] else args.get("--loglevel", "INFO")
    coloredlogs.install(
        level=int(level) if level.isdigit() else level,
        stream=stream,
        logger=logger)

    # if args['logout']:
    #     if not os.path.exists(InstaLooter.COOKIE_FILE):
    #         hues.error('Cookie file not found.')
    #         return 1
    #     InstaLooter().logout()
    #     hues.success('Logged out.')
    #     return 0

    # elif args['login']:
    #     try:
    #         args['--username'] = six.moves.input('Username: ')
    #         login(InstaLooter(), args)
    #         return 0
    #     except ValueError as ve:
    #         console.error(ve)
    #         if args["--traceback"]:
    #            traceback.print_exc()
    #         return 1

    if args['-W'] not in WARNING_ACTIONS:
        _print("Unknown warning action:", args['-W'])
        _print("    available actions:", ', '.join(WARNING_ACTIONS))
        return 1

    # if args['batch']:
    #     with open(args['<batch_file>']) as batch_file:
    #         batch_runner = BatchRunner(batch_file)
    #     batch_runner.runAll()
    #     return 0

    with warnings.catch_warnings():
        warnings.simplefilter(args['-W'])

        if args['user']:
            looter_cls = ProfileLooter
            target = args['<profile>']
        elif args['hashtag']:
            looter_cls = HashtagLooter
            target = args['<hashtag>']
        elif args['post']:
            looter_cls = PostLooter
            target = args['<post_token>']
        else:
            raise NotImplementedError("TODO")

        looter = looter_cls(
            target,
            add_metadata=args['--add-metadata'],
            get_videos=args['--get-videos'],
            videos_only=args['--videos-only'],
            jobs=int(args['--jobs']) if args['--jobs'] is not None else 16,
            template=args['--template'],
            dump_json=args['--dump-json'],
            dump_only=args['--dump-only'],
            extended_dump=args['--extended-dump']
        )

        try:
            # login(looter, args)
            if args['--time']:
                timeframe = get_times_from_cli(args['--time'])
            else:
                timeframe = None
        except ValueError as ve:
            _print("invalid format for --time parameter:", args["--time"])
            _print("    (format is [D]:[D] where D is an ISO 8601 date)")
            return 1

        try:

            media_count = int(args['--num-to-dl']) if args['--num-to-dl'] else None

            logger.debug("Opening destination filesystem")
            dest_url = args.get('<directory>') or os.getcwd()
            dest_fs = fs.open_fs(dest_url, create=True)

            logger.info("Starting download of `{}`".format(target))
            n = looter.download(
                destination=dest_fs,
                media_count=media_count,
                timeframe=timeframe,
                new_only=args['--new'],
                pgpbar_cls=None if args['--quiet'] else TqdmProgressBar,
                dlpbar_cls=None if args['--quiet'] else TqdmProgressBar)

            if n:
                logger.log(logging.SUCCESS,
                    "Downloaded {} media{} !".format(n, "s" if n > 1 else ""))

        except (Exception, KeyboardInterrupt) as e:
            from ._utils.threadutils import threads_force_join, threads_count

            # Show error traceback if any
            if not isinstance(e, KeyboardInterrupt):
                logger.fatal(e)
                if args["--traceback"]:
                    traceback.print_exc()
            else:
                logger.fatal("Interrupted")

            # Close remaining threads spawned by InstaLooter.download
            count = threads_count()
            if count:
                logger.info("Terminating {} remaining workers...".format(count))
                threads_force_join()

            # Return the error number if any
            errno = e.errno if hasattr(e, "errno") else None
            return errno if errno is not None else 1

        else:
            return 0

        finally:
            logger.debug("Closing destination filesystem")
            try:
                dest_fs.close()
            except Exception:
                pass
