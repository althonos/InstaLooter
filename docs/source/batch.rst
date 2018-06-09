Batch mode
==========

``instaLooter`` supports a batch mode for use cases that are more requiring than
just download from a profile once or twice. To use it, you must specify a
*batch config file* to the CLI. The file is in the Python configuration format,
very close to the Windows **INI** format.

Format
------
A *config file* contains at least one section, but can contain more if needed.
A section is organised as shown below, with a header and key-value pairs using
the ``=`` sign:

.. code-block:: ini

   [my section header]
   key = value
   other_key = other_value

Specifying targets
------------------

Users can be specified in the *users* parameter of each section, and hashtags
in the *hashtags* parameter. Those sections take a ``key: value`` pair per line,
where *key* is the name of the user, and *value* the path to the directory where
the medias will be downloaded. For instance:

.. code-block:: ini

   [Video Games]
   users =
       borderlands: /tmp/borderlands
       ffxv: /tmp/ffxv
   hashtags =
       nierautomata: /tmp/nier

   [Music]
   users =
      perm36 : ~/Music/Perm36


Logging in
----------

Each section can be provided with a ``username`` and a ``password`` parameter:

* if none are given, the scraping is done anonymously or using the last session
  you logged with (through ``instaLooter login`` for instance, or the session
  of the previous section).
* if only ``username`` is given, ``instaLooter`` will interactively ask for the
  associated password and then login.
* if both ``username`` and ``password`` are given, then ``instaLooter`` will
  logout from any previous session and login quietly.


Passing parameters
------------------

Each section can be given the same parameters as the command line:

``add-metadata``
  set to *True* to add metadata to the downloaded images
``get-videos``
  set to *True* to download videos as well as images
``jobs``
  the number of threads to use, defaults to ``16``
``template``
  the template to use, without quotes, defaults to ``{id}``
``videos-only``
  set to *True* to download only videos
``quiet``
  set to *True* to hide the progress bar
``new``
  set to *True* to only download new medias
``num-to-dl``
  the number of images to download
``dump-json``
  set to *True* to dump metadata in JSON format
``dump-only``
  set to *True* to only dump metadata, not downloading anything.
``extended-dump``
  set to *True* to fetch additional information when dumping metadata.

For instance, to download 3 new videos from ``#funny`` and ``#nsfw``:

.. code-block:: ini

   [Vids]
   videos-only = true
   new = true
   num-to-dl = 3
   hashtags =
       funny: ~/Videos
       nsfw: ~/Videos


Running the program
-------------------

Simply run the following command

.. code-block:: console

  instaLooter batch /path/to/your/batch.ini


Bugs
----

.. warning::

   This feature may not be completely functional yet ! I would say that it is
   still in beta, were the whole ``instaLooter`` program not in beta too **:D**.

Please report any bugs caused by this feature to the `Github
issue tracker <https://github.com/althonos/InstaLooter/issues>`_, adding the
configuration file as an attachment!
