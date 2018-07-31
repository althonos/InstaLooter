# coding: utf-8
"""Implementation of the main program executable.

Warning:
    Only `.cli.main` and `.cli.logger` are guaranteed to be stable, do not
    rely on any other member from this package !
"""
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
import verboselogs

from .. import __version__
from ..looters import InstaLooter, HashtagLooter, ProfileLooter, PostLooter
from ..pbar import TqdmProgressBar
from ..batch import BatchRunner, logger as batch_logger

from . import logutils
from .constants import HELP, USAGE, WARNING_ACTIONS
from .time import get_times_from_cli
from .login import login, logger as login_logger


__all__ = ["main", "logger"]


#: A `~logging.Logger` instance used within the `.cli` module.
logger = verboselogs.VerboseLogger(__name__)


@logutils.wrap_warnings(logger)
def main(argv=None, stream=None):
    """Run from the command line interface.

    Arguments:
        argv (list): The positional arguments to read. Defaults to
            `sys.argv` to use CLI arguments.
        stream (~io.IOBase): A file where to write error messages.
            Leave to `None` to use the `~coloredlogs.StandardErrorHandler`
            for logs, and `sys.stderr` for error messages.

    Returns:
        int: An error code, or 0 if the program executed successfully.
    """

    _print = functools.partial(print, file=stream or sys.stderr)

    # Parse command line arguments
    try:
        args = docopt.docopt(
            HELP, argv, version='instalooter {}'.format(__version__))
    except docopt.DocoptExit as de:
        _print(de)
        return 1

    # Print usage and exit if required (docopt does not do this !)
    if args['--usage']:
        _print(USAGE)
        return 0

    # Set the loggers up with the requested logging level
    level = "ERROR" if args['--quiet'] else args.get("--loglevel", "INFO")
    for logger_ in (logger, login_logger, batch_logger):
        coloredlogs.install(
            level=int(level) if level.isdigit() else level,
            stream=stream,
            logger=logger_)

    # Check the requested logging level
    if args['-W'] not in WARNING_ACTIONS:
        _print("Unknown warning action:", args['-W'])
        _print("    available actions:", ', '.join(WARNING_ACTIONS))
        return 1

    with warnings.catch_warnings():
        warnings.simplefilter(args['-W'])

        try:
            # Run in batch mode
            if args['batch']:
                # Load the batch configuration from the given file
                with open(args['<batch_file>']) as batch_file:
                    batch_runner = BatchRunner(batch_file, args)
                # Run the batch
                batch_runner.run_all()
                return 0

            # Login if requested
            if args['login']:
                try:
                    if not args['--username']:
                        args['--username'] = six.moves.input('Username: ')
                    login(args)
                    return 0
                except ValueError as ve:
                    logger.error("%s", ve)
                    if args["--traceback"]:
                       traceback.print_exc()
                    return 1

            # Logout if requested
            if args['logout']:
                if InstaLooter._cachefs.exists(InstaLooter._COOKIE_FILE):
                    InstaLooter._logout()
                    logger.success('Logged out.')
                else:
                    warnings.warn('Cookie file not found.')
                return 0

            # Normal download mode:
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

            # Instantiate the looter
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

            # Attempt to login and extract the timeframe
            if args['--username']:
                login(args)
            if args['--num-to-dl']:
                args['--num-to-dl'] = int(args['--num-to-dl'])
            try:
                if args['--time'] is not None:
                    args['--time'] = get_times_from_cli(args['--time'])
            except ValueError as ve:
                _print("invalid format for --time parameter:", args["--time"])
                _print("    (format is [D]:[D] where D is an ISO 8601 date)")
                return 1

            logger.debug("Opening destination filesystem")
            dest_url = args.get('<directory>') or os.getcwd()
            dest_fs = fs.open_fs(dest_url, create=True)

            logger.notice("Starting download of `%s`", target)
            n = looter.download(
                destination=dest_fs,
                media_count=args['--num-to-dl'],
                timeframe=args['--time'],
                new_only=args['--new'],
                pgpbar_cls=None if args['--quiet'] else TqdmProgressBar,
                dlpbar_cls=None if args['--quiet'] else TqdmProgressBar)
            if n > 1:
                logger.success("Downloaded %i posts.", n)
            elif n == 1:
                logger.success("Downloaded %i post.", n)

        except (Exception, KeyboardInterrupt) as e:
            from .threadutils import threads_force_join, threads_count
            # Show error traceback if any
            if not isinstance(e, KeyboardInterrupt):
                logger.critical("%s", e)
                if args["--traceback"]:
                    traceback.print_exc()
            else:
                logger.critical("Interrupted")
            # Close remaining threads spawned by InstaLooter.download
            count = threads_count()
            if count:
                logger.notice("Terminating %i remaining workers...", count)
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
