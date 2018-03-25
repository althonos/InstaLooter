API Reference
==============

.. toctree::
   :hidden:

   looters
   cli
   medias
   pages
   batch
   pbar
   worker


Main
----

.. rubric:: Looters (`instalooter.looters`)

.. currentmodule:: instalooter.looters

.. autosummary::
    :nosignatures:

    InstaLooter
    HashtagLooter
    ProfileLooter
    PostLooter


.. rubric:: Command Line Interface  (`instalooter.cli`)

.. currentmodule:: instalooter.cli

.. autosummary::

   main


.. rubric:: Batch Runner (`instalooter.batch`)

.. currentmodule:: instalooter.batch

.. autosummary::
   :nosignatures:

   BatchRunner


Iterators
---------

.. rubric:: Medias Iterators (`instalooter.medias`)

.. currentmodule:: instalooter.medias

.. autosummary::
    :nosignatures:

    MediasIterator
    TimedMediasIterator


.. rubric:: Pages Iterators (`instalooter.pages`)

.. currentmodule:: instalooter.pages

.. autosummary::
    :nosignatures:

    PageIterator
    HashtagIterator
    ProfileIterator


Miscellaneous
-------------

.. rubric:: Progress Bars (`instalooter.pbar`)

.. currentmodule:: instalooter.pbar

.. autosummary::
    :nosignatures:

    ProgressBar
    TqdmProgressBar


.. rubric:: Background Downloader (`instalooter.worker`)

.. currentmodule:: instalooter.worker

.. autosummary::
    :nosignatures:

    InstaDownloader
