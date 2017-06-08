Usage
=====

.. toctree::

instaLooter provides a command line interface, that you can call with
the ``instaLooter`` command.

.. note::

   In some cases, the ``instaLooter`` command is not added into
   the ``$PATH`` after installation. It is possible to perform
   all the following actions nevertheless by replacing occurences
   of ``instaLooter`` with ``python -m instaLooter`` (or
   ``python3 -m instaLooter``).

Command Line Interface
----------------------

Download pictures/videos from the profile of a single user:

.. code-block:: console

   $ instaLooter <username> [<directory>] [options]


Download pictures/videos tagged with a given *#hashtag*:

.. code-block:: console

   $ instaLooter hashtag <hashtag> <directory> [options]

Download pictures/videos from a single post:

.. code-block:: console

   $ instaLooter post <post_token> <directory> [options]


Positional Arguments
--------------------

``username``
  the username of the Instagram profile to download pictures/videos from.

``hashtag``
  the hashtag to download pictures/videos from.

``post_token``
  the URL or the code of the post to download.

``directory``
  the directory in which to download pictures/videos. Optional for
  profile download, will then use current directory.


Options - Credentials:
----------------------

``-u USER, --username USER``
  The username to connect to Instagram with.

``-p PASS, --password PASS``
  The password to connect to Instagram with (will be asked in the shell
  if the ``--username`` option was given without the corresponding
  ``--password``).

Options - Files:
----------------

``-n NUM, --num-to-dl NUM``
  Maximum number of new files to download

``-j JOBS, --jobs JOBS``
  Number of parallel threads to use to download files **[default: 16]**

``-T TMPL, --template TMPL``
  A filename template to use to write the files (see :ref:`Template`).
  **[default: {id}]**

``-v, --get-videos``
  Get videos as well as photos

``-V, --videos-only``
  Get videos only (implies ``--get-videos``)

``-N, --new``
  Only look for files newer than the ones in the destination directory
  (faster).

``-m, --add-metadata``
  Add date and caption metadata to downloaded pictures (requires
  `PIL <http://www.pythonware.com/products/pil/>`_ or
  `Pillow <https://python-pillow.org/>`_ as well as
  `piexif <https://pypi.python.org/pypi/piexif>`_).

``-t TIME, --time TIME``
  The time limit within which to download pictures and video
  (see :ref:`Time`)

Options - Miscellaneous:
------------------------

``-q, --quiet``
  Do not produce any output

``-h, --help``
  Display the help message

``--version``
  Show program version and quit

``--traceback``
  Print error traceback if any (debug).

``-W WARNINGCTL``
  Change warning behaviour (same as ``python -W``) **[default: default]**


.. _Template:

Template
--------

The default filename of the pictures and videos on Instagram doesn't show
anything about the file you just downloaded. But using the ``-t`` argument
allows you to give instaLooter a filename template, using the following
format with brackets-enclosed (``{}``) variable names among:

- ``id``\*\² and ``code``\² of the instagram id of the media
- ``ownerid``\*, ``username`` and ``fullname`` of the owner
- ``datetime``\*: the date and time of the post (YYYY-MM-DD hh:mm:ss)
- ``date``\*: the date of the post (YYYY-MM-DD)
- ``width``\* and ``height``\*
- ``likescount``\* and ``commentscount``\*

:\*:
   use these only to quicken download, since fetching the others may take
   a tad longer (in particular in hashtag download mode).

:\²:
   use at least one of these in your filename to make sure the generated
   filename is unique.

Examples of acceptable values:

.. code-block:: console

    $ instaLooter <profile> -T {username}.{datetime}
    $ instaLooter <profile> -T {username}-{likescount}-{width}x{height}.{id}
    $ instaLooter <profile> -T {username}.{code}.something_constant


.. _Time:

Time
----

The ``--time`` parameter can be given either a combination of start and stop
date in ISO format (e.g. ``2016-12-21:2016-12-18``, ``2015-03-07:``,
``:2016-08-02``) or a special value among: *thisday*, *thisweek*, *thismonth*,
*thisyear*.

Edges are included in the time frame, so if using the following value:
``--time 2016-05-10:2016-04-03``, then all medias will be downloaded
including the ones posted the 10th of May 2016 and the 3rd of April 2016.

.. _Credentials:

Credentials
-----------

The ``--username`` and ``--password`` parameters can be used to log to
Instagram. This allows you to download pictures/videos from private profiles
you are following. You can either provide your password directly
or type it in later for privacy purposes.

.. code-block:: console

   $ instaLooter ... --username USERNAME --password PASSWORD
   $ instaLooter ... --username USERNAME
   Password: # type PASSWORD privately here
