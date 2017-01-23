Usage
=====

.. toctree::

instaLooter - Another API-less Instagram pictures and videos downloader

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

   $ instaLooter hashtag <hashtag> [<directory>] [options]


Positional Arguments
--------------------

``username``
  the username of the Instagram profile to download pictures/videos from.

``hashtag``
  the hashtag to download pictures/videos from.

``optional``
  the directory in which to download pictures/videos. If not given, the current
  directory is used.


Optional Arguments
------------------

``-n NUM, --num NUM``
  the maximum number of new files to download

``-j JOBS, --jobs JOBS``
  the number of parallel threads to use to download files. A value greater than
  12 is advised since each page has 12 single medias on it. **[default: 16]**

``-T TMPL, --template TMPL``
  A filename template to use to write files (see :ref:`Template`).
  **[default: {id}]**

``-v, --get-videos``
  Get videos as well as pictures.

``-N, --new``
  Only download files newer than the ones in the destination directory (faster
  if you use instaLooter to sync a local copy of a profile). This used filenames
  to check for present and missing files, so make sure you use the same template
  as the older runs.

``-m, --add-metadata``
  Add date, caption and authorship metadata to downloaded pictures. Requires
  ``PIL`` or ``Pillow`` as well as ``piexif``.

``-q, --quiet``
  Do not display and progress bar output.

``-t TIME, --time TIME``
  The time limit within which to download pictures and videos (see :ref:`Time`).

``-c CRED, --credentials CRED``
  Credentials to login to Instagram with if needed (see :ref:`Credentials`).

``-h, --help``
  Show the complete help message.

``--version``
  Show version and exit.

.. _Template:

Template
--------

The default filename of the pictures and videos on Instagram doesn't show
anything about the file you just downloaded. But using the ``-t`` argument
allows you to give instaLooter a filename template, using the following
format with brackets-enclosed (``{}``) variable names among:

- ``id``\*\² and ``code``\² of the instagram id of the media
- ``ownerid``\*, ``username`` and ``fullname`` of the owner
- ``datetime``\*\²: the date and time of the post (YYYY-MM-DD hh:mm:ss)
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

The ``-c`` parameter can be used to log to Instagram. This allows you to
download pictures/videos from private profiles you are following. You can
either provide your password directly or type it in later for privacy
purposes.

.. code-block:: console

   $ instaLooter ... -c MYLOGIN:MYPASSWORD
   $ instaLooter ... -c MYLOGIN
   Password: # type MYPASSWORD privately here
