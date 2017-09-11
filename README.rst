InstaLooter |Starme|
====================

*Not all treasure's silver and gold, mate.*

|build| |repo| |versions| |format| |coverage| |doc| |requirements| |grade| |license|

InstaLooter is a program that can download any picture or video associated
from an Instagram profile, without any API access. It can be seen as a
re-implementation of the now deprecated `InstaRaider <https://github.com/akurtovic/InstaRaider>`_
developed by `@akurtovic <https://github.com/akurtovic>`_.

.. |Starme| image:: https://img.shields.io/github/stars/althonos/InstaLooter.svg?style=social&label=Star&maxAge=3600
   :target: https://github.com/althonos/InstaLooter

.. |repo| image:: https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=3600&style=flat-square
   :target: https://github.com/althonos/InstaLooter

.. |versions| image:: https://img.shields.io/pypi/v/instaLooter.svg?maxAge=3600&style=flat-square
   :target: https://pypi.python.org/pypi/instaLooter

.. |format| image:: https://img.shields.io/pypi/format/instaLooter.svg?maxAge=3600&style=flat-square
   :target: https://pypi.python.org/pypi/instaLooter

.. |grade| image:: https://img.shields.io/codacy/grade/9b8c7da6887c4195b9e960cb04b59a91/master.svg?maxAge=3600&style=flat-square
   :target: https://www.codacy.com/app/althonos/InstaLooter/dashboard

.. |coverage| image:: https://img.shields.io/codecov/c/github/althonos/InstaLooter/master.svg?maxAge=3600&style=flat-square
   :target: https://codecov.io/gh/althonos/InstaLooter

.. |build| image:: https://img.shields.io/travis/althonos/InstaLooter/master.svg?label=travis-ci&maxAge=3600&style=flat-square
   :target: https://travis-ci.org/althonos/InstaLooter/

.. |doc| image:: https://readthedocs.org/projects/instalooter/badge/?version=latest&maxAge=3600&style=flat-square
   :target: http://instalooter.readthedocs.io/en/latest/?badge=latest

.. |requirements| image:: https://img.shields.io/requires/github/althonos/InstaLooter/master.svg?style=flat-square&maxAge=3600
   :target: https://requires.io/github/althonos/InstaLooter/requirements/?branch=master

.. |health| image:: https://landscape.io/github/althonos/InstaLooter/master/landscape.svg?style=flat-square&maxAge=3600
   :target: https://landscape.io/github/althonos/InstaLooter/master

.. |license| image:: https://img.shields.io/pypi/l/InstaLooter.svg?maxAge=3600&style=flat-square
   :target: https://choosealicense.com/licenses/gpl-3.0/


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


Installation
------------

InstaLooter is available on PyPI to install with ``pip``. If you are not
familiar with the package management of the Python ecosystem, please see the
`Installation page <http://instalooter.readthedocs.io/en/latest/install.html>`_
of the `online documentation <http://instalooter.readthedocs.io/en/latest/index.html>`_.
Yet, you will probably end up using the following command::

  pip install --user instaLooter


Usage
-----

InstaLooter comes with its CLI:

.. code-block:: console

    $ instaLooter <username> [<directory>] [options]
    $ instaLooter (hashtag <hashtag> <directory> [options]
    $ instaLooter post <post_token> <directory> [options]
    $ instaLooter batch <batch_file>


Logging in and out
------------------
There are two ways to login on Instagram through *instaLooter*:

* use the `login` subcommand (``instaLooter login``) to interactively login
  using your username and password.
* give a ``--username`` (and, if you want, a ``--password``) argument to any of
  the download commands.

In both cases, a session cookie will be created in the system temporary folder.
To delete it and close your session on the server, use the ``logout``
subcommand.


Examples
--------

Download all pictures from the *instagram* profile in the current directory::

    $ instaLooter instagram

Download the latest 20 pictures or videos tagged with *python* to */tmp*::

    $ instaLooter hashtag python /tmp -n 20 -v -c MYLOGIN

Download a single post from an url in the current directory::

    $ instaLooter post "https://www.instagram.com/p/BFB6znLg5s1/" .

Use a configuration file to download from several account using custom parameters 
(see `Batch mode <http://instalooter.readthedocs.io/en/latest/batch.html>`_)::

    $ instaLooter batch /path/to/a/config/file.ini

See more on the `Usage page <http://instalooter.readthedocs.io/en/latest/usage.html>`_
of the `online documentation <http://instalooter.readthedocs.io/en/latest/index.html>`_.


.. |PyPI requests| image:: https://img.shields.io/pypi/v/requests.svg?maxAge=3600&style=flat-square
   :target: https://pypi.python.org/pypi/requests

.. |PyPI BeautifulSoup| image:: https://img.shields.io/pypi/v/beautifulsoup4.svg?maxAge=3600&style=flat-square
   :target: https://pypi.python.org/pypi/beautifulsoup4

.. |PyPI six| image:: https://img.shields.io/pypi/v/six.svg?maxAge=3600&style=flat-square
   :target: https://pypi.python.org/pypi/six

.. |PyPI progressbar2| image:: https://img.shields.io/pypi/v/progressbar2.svg?maxAge=3600&style=flat-square
   :target: https://pypi.python.org/pypi/progressbar2

.. |PyPI docopt| image:: https://img.shields.io/pypi/v/docopt.svg?maxAge=3600&style=flat-square
   :target: https://pypi.python.org/pypi/docopt/

.. |PyPI dateutil| image:: https://img.shields.io/pypi/v/python-dateutil.svg?maxAge=3600&style=flat-square
   :target: https://pypi.python.org/pypi/python-dateutil/

.. |PyPI hues| image:: https://img.shields.io/pypi/v/hues.svg?maxAge=3600&style=flat-square
   :target: https://pypi.python.org/pypi/hues/

.. |Source requests| image:: https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=3600&style=flat-square
   :target: https://github.com/kennethreitz/requests

.. |Source docopt| image:: https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=3600&style=flat-square
   :target: https://github.com/docopt/docopt

.. |Source dateutil| image:: https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=3600&style=flat-square
   :target: https://github.com/dateutil/dateutil/

.. |Source BeautifulSoup| image:: https://img.shields.io/badge/source-Launchpad-orange.svg?maxAge=3600&style=flat-square
   :target: https://launchpad.net/beautifulsoup

.. |Source six| image:: https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=3600&style=flat-square
   :target: https://github.com/benjaminp/six

.. |Source progressbar2| image:: https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=3600&style=flat-square
   :target: https://github.com/WoLpH/python-progressbar

.. |Source hues| image:: https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=3600&style=flat-square
   :target: https://github.com/prashnts/hues

.. |License requests| image:: https://img.shields.io/pypi/l/requests.svg?maxAge=3600&style=flat-square
   :target: https://choosealicense.com/licenses/apache-2.0/

.. |License BeautifulSoup| image:: https://img.shields.io/pypi/l/BeautifulSoup4.svg?maxAge=3600&style=flat-square
   :target: https://choosealicense.com/licenses/mit/

.. |License six| image:: https://img.shields.io/pypi/l/BeautifulSoup4.svg?maxAge=3600&style=flat-square
   :target: https://choosealicense.com/licenses/mit/

.. |License progressbar2| image:: https://img.shields.io/pypi/l/progressbar2.svg?maxAge=3600&style=flat-square
   :target: https://choosealicense.com/licenses/bsd-3-clause/

.. |License docopt| image:: https://img.shields.io/pypi/l/docopt.svg?maxAge=3600&style=flat-square
   :target: https://choosealicense.com/licenses/mit/

.. |License dateutil| image:: https://img.shields.io/pypi/l/python-dateutil.svg?maxAge=3600&style=flat-square
   :target: https://choosealicense.com/licenses/bsd-3-clause/

.. |License hues| image:: https://img.shields.io/pypi/l/hues.svg?maxAge=3600&style=flat-square
   :target: https://choosealicense.com/licenses/mit/
