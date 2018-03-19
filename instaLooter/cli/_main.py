# coding: utf-8
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import getpass
import warnings
import traceback

import docopt
import fs
import six

from .. import __version__
from ..looter import HashtagLooter, ProfileLooter, PostLooter
from ..pbar import TqdmProgressBar
# from ..batch import BatchRunner

from ._utils.constants import HELP, USAGE, WARNING_ACTIONS
from ._utils.console import console, wrap_warnings
from ._utils.time import get_times_from_cli


__all__ = ["main"]


@wrap_warnings
def main(argv=None):
    """Run from the command line interface.
    """

    try:
        args = docopt.docopt(
            HELP, argv,
            version='instaLooter {}'.format(__version__)
        )
    except docopt.DocoptExit as de:
        print(de)
        return 1

    if args['--usage']:
        print(USAGE)
        return 0
    # argv_positional = [param for param in argv if not param.startswith("-")]
    # if argv_positional[0] in ("post", "hashtag") and len(argv_positional) < 3:
    #     print(usage())
    #     return 1

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
        print("Unknown warning action: {}".format(args['-W']))
        print("   available action: {}".format(', '.join(WARNING_ACTIONS)))
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
            # if args['--time']:
            #     timeframe = get_times_from_cli(args['--time'])
            # else:
            timeframe = None
        except ValueError as ve:
            console.error(ve)
            if args["--traceback"]:
               traceback.print_exc()
            return 1

        try:

            media_count = int(args['--num-to-dl']) if args['--num-to-dl'] else None

            console.info("Opening destination filesystem")
            dest_url = args.get('<directory>') or os.getcwd()
            dest_fs = fs.open_fs(dest_url, create=True)

            console.info("Starting download")
            n = looter.download(
                destination=dest_fs,
                media_count=media_count,
                timeframe=timeframe,
                new_only=args['--new'],
                pgpbar_cls=None if args['--quiet'] else TqdmProgressBar,
                dlpbar_cls=None if args['--quiet'] else TqdmProgressBar,
            )

            if n:
                console.success("Downloaded {} media{} !".format(
                    n, "s" if n > 1 else ""))

        except (Exception, KeyboardInterrupt) as e:
            from ._utils.threadutils import threads_force_join

            # Show error traceback if any
            if not isinstance(e, KeyboardInterrupt):
                console.error(e)
                if args["--traceback"]:
                    traceback.print_exc()
            else:
                console.error("Interrupted")

            # Close remaining threads spawned by InstaLooter.download
            console.info("Waiting for workers to terminate...")
            threads_force_join()

            # Return the error number if any
            errno = e.errno if hasattr(e, "errno") else None
            return errno if errno is not None else 1

        else:
            return 0

        finally:
            console.info("Closing destination filesystem")
            try:
                dest_fs.close()
            except Exception:
                pass
