InstaLooter
===========

InstaLooter is a downloader that can download any picture or video associated
from an Instagram profile. It can be seen as a re-implementation of the now
deprecated `InstaRaider <https://github.com/akurtovic/InstaRaider>`_ developed by
`@akurtovic <https://github.com/akurtovic>`_.

This implementation only requires `BeautifulSoup <https://pypi.python.org/pypi/beautifulsoup4>`_
for html parsing, `six <https://pypi.python.org/pypi/six>`_ for version compatibility, and
`progressbar2 <https://pypi.python.org/pypi/progressbar2>`_ for the output.

Usage
-----

.. code::

    instaLooter [options] username directory


Additional Parameters
^^^^^^^^^^^^^^^^^^^^^

-n NUM_TO_DOWNLOAD
    number of new posts to download (if not specified all posts are downloaded)

-m, --add-metadata
    add date and caption metadata to downloaded pictures

-v, --get-videos
    also download videos

-j JOBS, --jobs JOBS
    the number of parallel threads to use to download files (default is 16)

-q, --quiet
    do not produce any output


Installation
------------

Install with pip:

.. code::

    pip install instaLooter
