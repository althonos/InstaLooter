InstaLooter |Starme|
====================

InstaLooter is a downloader that can download any picture or video associated
from an Instagram profile. It can be seen as a re-implementation of the now
deprecated `InstaRaider <https://github.com/akurtovic/InstaRaider>`_ developed by
`@akurtovic <https://github.com/akurtovic>`_.



Requirements
------------

+-------------------+----------------------------+----------------------+------------------------+-------------------------+
| **requests**      |  HTTP handling             | |PyPI requests|      | |Source requests|      | |License requests|      |
+-------------------+----------------------------+----------------------+------------------------+-------------------------+
| **BeautifulSoup** |  HTML parsing              | |PyPI BeautifulSoup| | |Source BeautifulSoup| | |License BeautifulSoup| |
+-------------------+----------------------------+----------------------+------------------------+-------------------------+
| **six**           |  Python 2/3 compatibility  | |PyPI six|           | |Source six|           | |License six|           |
+-------------------+----------------------------+----------------------+------------------------+-------------------------+
| **progressbar2**  |  Dynamic output in CLI     | |PyPI progressbar2|  | |Source progressbar2|  | |License progressbar2|  |
+-------------------+----------------------------+----------------------+------------------------+-------------------------+

Usage
-----

InstaLooter comes with its CLI::

    $ instaLooter [options] username directory
    
Arguments
^^^^^^^^^
- ``username``
    the username of the instagram account to download pictures and videos from.
- ``directory``
    the directory to download files into.

Options
^^^^^^^
- ``-n NUM_TO_DOWNLOAD``
    number of maximum new posts to download (if not specified all posts are downloaded).
- ``-m, --add-metadata``
    add date and caption metadata to downloaded pictures (requires piexif and Pillow).
- ``-v, --get-videos``
    also download videos.
- ``-j JOBS, --jobs JOBS``
    the number of parallel threads to use to download files (defaults to 16). It is 
    advised to use a value of at least 12 as Instagram profile pages display 12 medias
    at a time in order to insure parallel download of all files.
- ``-q, --quiet``
    do not produce any output.


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

.. |PyPI requests| image:: https://img.shields.io/pypi/v/requests.svg
   :target: https://pypi.python.org/pypi/requests
  
.. |PyPI BeautifulSoup| image:: https://img.shields.io/pypi/v/beautifulsoup4.svg
   :target: https://pypi.python.org/pypi/beautifulsoup4

.. |PyPI six| image:: https://img.shields.io/pypi/v/six.svg
   :target: https://pypi.python.org/pypi/six
   
.. |PyPI progressbar2| image:: https://img.shields.io/pypi/v/progressbar2.svg
   :target: https://pypi.python.org/pypi/progressbar2
    
.. |Source requests| image:: https://img.shields.io/badge/source-GitHub-green.svg?maxAge=3600   
   :target: https://github.com/kennethreitz/requests

.. |Source BeautifulSoup| image:: https://img.shields.io/badge/source-Launchpad-orange.svg?maxAge=3600   
   :target: https://launchpad.net/beautifulsoup

.. |Source six| image:: https://img.shields.io/badge/source-Bitbucket-blue.svg?maxAge=3600
   :target: https://bitbucket.org/gutworth/six
   
.. |Source progressbar2| image:: https://img.shields.io/badge/source-GitHub-green.svg?maxAge=3600&width=40 
   :target: https://github.com/WoLpH/python-progressbar
   
.. |License requests| image:: https://img.shields.io/pypi/l/requests.svg  
   :target: https://opensource.org/licenses/Apache-2.0
   
.. |License BeautifulSoup| image:: https://img.shields.io/pypi/l/BeautifulSoup4.svg
   :target: https://opensource.org/licenses/MIT   
     
.. |License six| image:: https://img.shields.io/pypi/l/BeautifulSoup4.svg
   :target: https://opensource.org/licenses/MIT

.. |License progressbar2| image:: https://img.shields.io/pypi/l/progressbar2.svg
   :target: https://opensource.org/licenses/BSD-3-Clause
   
