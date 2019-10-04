# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import textwrap


WARNING_ACTIONS = {'error', 'ignore', 'always', 'default', 'module', 'once'}


HELP = textwrap.dedent(
    """
    instalooter - Another API-less Instagram media downloader

    Usage:
        instalooter (-h | --help | --version | --usage)
        instalooter batch <batch_file> [<directory>] [options]
        instalooter hashtag <hashtag> [<directory>] [options]
        instalooter user <profile> [<directory>] [options]
        instalooter post <post_token> [<directory>] [options]
        instalooter logout
        instalooter login [options]

    Arguments:
        <profile>                    The username of the profile to download
                                     pictures and optionally videos from.
        <hashtag>                    A hashtag to download pictures and
                                     optionally videos from.
        <post_token>                 Either the url or the code of a post to
                                     download the picture or video from.
        <directory>                  The directory in which to download files.
                                     Can actually be a Pyfilesystem2 FS URL
                                     (see http://pyfilesystem2.rtfd.io).
        <batch_file>                 The path to the batch file containing
                                     batch download instructions (see the
                                     online documentation).

    Options - Credentials:
        -u USER, --username USER     The username to connect to Instagram with.
        -p PASS, --password PASS     The password to connect to Instagram with
                                     (will be asked in the shell if the
                                     `--username`  option was given without
                                     the corresponding `--password`).

    Options - Files:
        -n NUM, --num-to-dl NUM      Maximum number of new files to download
        -j JOBS, --jobs JOBS         Number of parallel threads to use to
                                     download files. [default: 16]
        -T TMPL, --template TMPL     A filename template to use to write the
                                     files (see *Template*). [default: {id}]
        -v, --get-videos             Get videos as well as photos.
        -V, --videos-only            Get videos only. Implies `--get-videos`.
        -N, --new                    Only look for files newer than the ones
                                     in the destination directory (faster).
        -t TIME, --time TIME         The time limit within which to download
                                     pictures and video (see *Time*).

    Options - Metadata:
        -m, --add-metadata           Add date and caption metadata to downloaded
                                     pictures (requires PIL/Pillow and piexif).
        -d, --dump-json              Save metadata to a JSON file next to
                                     downloaded videos/pictures.
        -D, --dump-only              Save only the metadata and no video/picture.
                                     Implies `--dump-json`.
        -e, --extended-dump          Always dump the maximum amount of extracted
                                     information, at the cost of more time.

    Options - Miscellaneous:
        -l LEVEL, --loglevel LEVEL   The level of log to produce, as an
                                     integer or a level name. [default: INFO]
        -q, --quiet                  Do not display any output or progress
                                     bar. Implies `--loglevel ERROR`.
        -h, --help                   Display this message and quit.
        --version                    Show program version and quit.
        --traceback                  Print error traceback if any (use when
                                     reporting an issue on GitHub, please!).
        -W WARNINGCTL                Change warning behaviour (same as the
                                     Python `-W` flag). [default: default]

    Template:
        The default filename of the pictures and videos on Instagram doesn't
        show anything about the file you just downloaded. But using the -T
        argument allows you to give instalooter a filename template, using the
        the following format with brackets-enclosed ({}) variable names among:
        - ``id``*² and ``code``*² of the instagram id of the media
        - ``ownerid``*, ``username`` and ``fullname`` of the owner
        - ``datetime``*: the date and time of the post (YYYY-MM-DD hh:mm:ss)
        - ``date``*: the date of the post (YYYY-MM-DD)
        - ``width``* and ``height``*
        - ``likescount``* and ``commentscount``*

        ²: use at least one of these to make sure the generated file name
        is unique (``datetime`` is not unique anymore since multiple posts).

        *: use these only to quicken download, since fetching the others may
        take a tad longer (in particular in hashtag download mode).

        You are however to make sure that the generated filename is unique,
        so you should use at least id, code or datetime somewhere.
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
)


USAGE = next(s for s in HELP.split("\n\n") if s.startswith("Usage"))
