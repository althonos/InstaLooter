InstaLooter |Starme|
====================

*Not all treasure's silver and gold, mate.*

InstaLooter is a program that can download any picture or video associated
from an Instagram profile, without any API access. It can be seen as a
re-implementation of the now deprecated `InstaRaider <https://github.com/akurtovic/InstaRaider>`_
developed by `@akurtovic <https://github.com/akurtovic>`_.


Requirements
------------

+-------------------+----------------------------+----------------------+------------------------+-------------------------+
| **BeautifulSoup** |  HTML parsing              | |PyPI BeautifulSoup| | |Source BeautifulSoup| | |License BeautifulSoup| |
+-------------------+----------------------------+----------------------+------------------------+-------------------------+
| **docopt**        |  CLI arguments parsing     | |PyPI docopt|        | |Source docopt|        | |License docopt|        |
+-------------------+----------------------------+----------------------+------------------------+-------------------------+
| **progressbar2**  |  Dynamic output in CLI     | |PyPI progressbar2|  | |Source progressbar2|  | |License progressbar2|  |
+-------------------+----------------------------+----------------------+------------------------+-------------------------+
| **requests**      |  HTTP handling             | |PyPI requests|      | |Source requests|      | |License requests|      |
+-------------------+----------------------------+----------------------+------------------------+-------------------------+
| **six**           |  Python 2/3 compatibility  | |PyPI six|           | |Source six|           | |License six|           |
+-------------------+----------------------------+----------------------+------------------------+-------------------------+
| **dateutil**      |  Date manipulation         | |PyPI dateutil|      | |Source dateutil|      | |License dateutil|      |
+-------------------+----------------------------+----------------------+------------------------+-------------------------+
| **hues**          |  Colored output            | |PyPI hues|          | |Source hues|          | |License hues|          |
+-------------------+----------------------------+----------------------+------------------------+-------------------------+


Usage
-----

InstaLooter comes with its CLI::

    $ instaLooter <username> <directory> [options]
    $ instaLooter hashtag <hashtag> <directory> [options]

Arguments
^^^^^^^^^
- ``username``
    the username of the instagram account to download pictures and videos from.
- ``hashtag``
    the hashtag to download pictures and videos from.
- ``directory``
    the directory to download files into.

Options
^^^^^^^
- ``-n NUM, --num-to-dl NUM``
    number of maximum new posts to download (if not specified all
    posts are downloaded).
- ``-m, --add-metadata``
    add date and caption metadata to downloaded pictures (requires
    piexif and PIL/Pillow)
- ``-v, --get-videos``
    also download videos.
- ``-j JOBS, --jobs JOBS``
    the number of parallel threads to use to download files. It is
    advised to use a value of at least 12 as Instagram profile pages
    display 12 medias at a time in order to insure parallel download
    of all files. [default: 16]
- ``-c CRED, --credentials CRED``
    the login and password to use to login to Instagram, if needed
    (for instance: downloading medias from a private account you
    follow). [format: login[:password]]
- ``-q, --quiet``
    do not produce any output.
- ``-N, --new``
    stop the iteration through Instagram pages when a media on the page
    is found in the destination directory. This makes it faster when
    InstaLooter is used to maintain a local copy of an Instagram account
    and allows only getting the newest pictures/videos without re-checking
    the oldest.
- ``-t TIME, --time TIME``
    the timeframe within which to download pictures and videos
    [format: start:stop]. The parameter can be either a combination of
    start and stop date in ISO format (e.g. ``2016-12-21:2016-12-18``,
    ``2015-03-07:``, ``:2016-08-02``) or a special value among: ``thisday``,
    ``thisweek``, ``thismonth``, ``thisyear``. Edges are included in the time frame,
    so if using the following value: ``--time 2016-05-10:2016-04-03``,
    then all medias will be downloaded including the ones posted on the 10th
    of May 2016 and on the 3rd of April 2016.
- ``-T TMPL, --template TMPL``
    A filename template to use to write the files. [default: {id}]
    The default filename of the pictures and videos on Instagram doesn't show
    anything about the file you just downloaded. But using the -t argument
    allows you to give instaLooter a filename template, using the following
    format with brackets-enclosed (``{}``) variable names among:
        - ``id*`` and ``code*`` of the instagram id of the media
        - ``ownerid*``, ``username`` and ``fullname`` of the owner
        - ``datetime*``: the date and time of the post (YYYY-MM-DD hh:mm:ss)
        - ``date*``: the date of the post (YYYY-MM-DD)
        - ``width*`` and ``height*``
        - ``likescount*`` and ``commentscount*``

    *: use these only to quicken download, since fetching the others may take
    a tad longer (in particular in hashtag download mode).

    You are however to make sure that the generated filename is unique, so you
    should use at least id, code or datetime somewhere.
    Examples of acceptable values:
        - ``{username}.{datetime}``
        - ``{username}-{likescount}-{width}x{height}.{id}``
        - ``{username}.{datetime}.something_constant``



Installation
------------

From PyPI
^^^^^^^^^
.. code::

    $ pip install instaLooter  # requires super-user rights

From GitHub
^^^^^^^^^^^
.. code::

    $ git clone https://github.com/althonos/InstaLooter
    $ cd InstaLooter
    $ pip install .            # requires super-user rights


.. |Starme| image:: https://img.shields.io/github/stars/althonos/InstaLooter.svg?style=social&label=Star
   :target: https://github.com/althonos/InstaLooter

.. |PyPI requests| image:: https://img.shields.io/pypi/v/requests.svg?maxAge=3600
   :target: https://pypi.python.org/pypi/requests

.. |PyPI BeautifulSoup| image:: https://img.shields.io/pypi/v/beautifulsoup4.svg?maxAge=3600
   :target: https://pypi.python.org/pypi/beautifulsoup4

.. |PyPI six| image:: https://img.shields.io/pypi/v/six.svg?maxAge=3600
   :target: https://pypi.python.org/pypi/six

.. |PyPI progressbar2| image:: https://img.shields.io/pypi/v/progressbar2.svg?maxAge=3600
   :target: https://pypi.python.org/pypi/progressbar2

.. |PyPI docopt| image:: https://img.shields.io/pypi/v/docopt.svg?maxAge=3600
   :target: https://pypi.python.org/pypi/docopt/

.. |PyPI dateutil| image:: https://img.shields.io/pypi/v/python-dateutil.svg?maxAge=3600
   :target: https://pypi.python.org/pypi/python-dateutil/

.. |PyPI hues| image:: https://img.shields.io/pypi/v/hues.svg?maxAge=3600
   :target: https://pypi.python.org/pypi/hues/

.. |Source requests| image:: https://img.shields.io/badge/source-GitHub-green.svg?maxAge=3600
   :target: https://github.com/kennethreitz/requests

.. |Source docopt| image:: https://img.shields.io/badge/source-GitHub-green.svg?maxAge=3600
   :target: https://github.com/docopt/docopt

.. |Source dateutil| image:: https://img.shields.io/badge/source-GitHub-green.svg?maxAge=3600
   :target: https://github.com/dateutil/dateutil/

.. |Source BeautifulSoup| image:: https://img.shields.io/badge/source-Launchpad-orange.svg?maxAge=3600
   :target: https://launchpad.net/beautifulsoup

.. |Source six| image:: https://img.shields.io/badge/source-Bitbucket-blue.svg?maxAge=3600
   :target: https://bitbucket.org/gutworth/six

.. |Source progressbar2| image:: https://img.shields.io/badge/source-GitHub-green.svg?maxAge=3600
   :target: https://github.com/WoLpH/python-progressbar

.. |Source hues| image:: https://img.shields.io/badge/source-GitHub-green.svg?maxAge=3600
   :target: https://github.com/prashnts/hues

.. |License requests| image:: https://img.shields.io/pypi/l/requests.svg?maxAge=3600
   :target: https://opensource.org/licenses/Apache-2.0

.. |License BeautifulSoup| image:: https://img.shields.io/pypi/l/BeautifulSoup4.svg?maxAge=3600
   :target: https://opensource.org/licenses/MIT

.. |License six| image:: https://img.shields.io/pypi/l/BeautifulSoup4.svg?maxAge=3600
   :target: https://opensource.org/licenses/MIT

.. |License progressbar2| image:: https://img.shields.io/pypi/l/progressbar2.svg?maxAge=3600
   :target: https://opensource.org/licenses/BSD-3-Clause

.. |License docopt| image:: https://img.shields.io/pypi/l/docopt.svg?maxAge=3600
   :target: https://opensource.org/licenses/MIT

.. |License dateutil| image:: https://img.shields.io/pypi/l/python-dateutil.svg?maxAge=3600
   :target: https://opensource.org/licenses/BSD-3-Clause

.. |License hues| image:: https://img.shields.io/pypi/l/hues.svg?maxAge=3600
   :target: https://opensource.org/licenses/MIT
