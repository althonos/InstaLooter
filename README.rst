InstaLooter |starme|
====================

.. |starme| image:: https://img.shields.io/github/stars/althonos/InstaLooter.svg?style=social&label=Star
   :target: https://github.com/althonos/InstaLooter

*Not all treasure's silver and gold, mate.*

|build| |repo| |versions| |format| |coverage| |doc| |grade| |license|
|keepachangelog| |saythanks|


.. |build| image:: https://img.shields.io/travis/althonos/InstaLooter/master.svg?label=travis-ci&style=flat-square
   :target: https://travis-ci.org/althonos/InstaLooter/

.. |repo| image:: https://img.shields.io/badge/source-GitHub-303030.svg?style=flat-square
   :target: https://github.com/althonos/InstaLooter

.. |versions| image:: https://img.shields.io/pypi/v/instalooter.svg?style=flat-square
   :target: https://pypi.org/project/instalooter

.. |format| image:: https://img.shields.io/pypi/format/instalooter.svg?style=flat-square
   :target: https://pypi.org/project/instalooter

.. |grade| image:: https://img.shields.io/codacy/grade/9b8c7da6887c4195b9e960cb04b59a91/master.svg?style=flat-square
   :target: https://www.codacy.com/app/althonos/InstaLooter/dashboard

.. |coverage| image:: https://img.shields.io/codecov/c/github/althonos/InstaLooter/master.svg?style=flat-square
   :target: https://codecov.io/gh/althonos/InstaLooter

.. |doc| image:: https://img.shields.io/readthedocs/instalooter.svg?style=flat-square
   :target: http://instalooter.readthedocs.io/en/latest/?badge=latest

.. .. |requirements| image:: https://img.shields.io/requires/github/althonos/InstaLooter/master.svg?style=flat-square
..    :target: https://requires.io/github/althonos/InstaLooter/requirements/?branch=master

.. .. |health| image:: https://landscape.io/github/althonos/InstaLooter/master/landscape.svg?style=flat-square
..    :target: https://landscape.io/github/althonos/InstaLooter/master

.. |license| image:: https://img.shields.io/pypi/l/instalooter.svg?style=flat-square
   :target: https://choosealicense.com/licenses/gpl-3.0/

.. |keepachangelog| image:: https://img.shields.io/badge/keep%20a-changelog-8A0707.svg?maxAge=86400&style=flat-square
   :target: http://keepachangelog.com/

.. |saythanks| image:: https://img.shields.io/badge/say-thanks!-1EAEDB.svg?maxAge=86400&style=flat-square
   :target: https://saythanks.io/to/althonos


InstaLooter is a program that can download any picture or video associated
from an Instagram profile, without any API access. It can be seen as a
re-implementation of the now deprecated `InstaRaider <https://github.com/akurtovic/InstaRaider>`_
developed by `@akurtovic <https://github.com/akurtovic>`_.

``v1.0.0`` *was completely rewrote from scratch, and as such, will
probably break compatibility with your homemade scripts. Meanwhile, great care
was taken to keep the CLI as consistent as possible with the previous versions,
so it'll hopefully feel like home.*


Requirements
------------

+--------------------+----------------------------+----------------------+------------------------+-------------------------+
| **coloredlogs**    |  Colored output            | |PyPI coloredlogs|   | |Source coloredlogs|   | |License coloredlogs|   |
+--------------------+----------------------------+----------------------+------------------------+-------------------------+
| **dateutil**       |  Date manipulation         | |PyPI dateutil|      | |Source dateutil|      | |License dateutil|      |
+--------------------+----------------------------+----------------------+------------------------+-------------------------+
| **docopt**         |  CLI arguments parsing     | |PyPI docopt|        | |Source docopt|        | |License docopt|        |
+--------------------+----------------------------+----------------------+------------------------+-------------------------+
| **fs**             |  Filesystem handling       | |PyPI fs|            | |Source fs|            | |License fs|            |
+--------------------+----------------------------+----------------------+------------------------+-------------------------+
| **requests**       |  HTTP handling             | |PyPI requests|      | |Source requests|      | |License requests|      |
+--------------------+----------------------------+----------------------+------------------------+-------------------------+
| **six**            |  Python 2/3 compatibility  | |PyPI six|           | |Source six|           | |License six|           |
+--------------------+----------------------------+----------------------+------------------------+-------------------------+
| **tenacity**       |  Retry until success       | |PyPI tenacity|      | |Source tenacity|      | |License tenacity|      |
+--------------------+----------------------------+----------------------+------------------------+-------------------------+
| **tqdm**           |  Dynamic output in CLI     | |PyPI tqdm|          | |Source tqdm|          | |License tqdm|          |
+--------------------+----------------------------+----------------------+------------------------+-------------------------+
| **verboselogs**    |  More detailed logs        | |PyPI verboselogs|   | |Source verboselogs|   | |License verboselogs|   |
+--------------------+----------------------------+----------------------+------------------------+-------------------------+


.. |PyPI coloredlogs| image:: https://img.shields.io/pypi/v/coloredlogs.svg?style=flat-square
   :target: https://pypi.org/project/coloredlogs

.. |PyPI dateutil| image:: https://img.shields.io/pypi/v/python-dateutil.svg?style=flat-square
   :target: https://pypi.org/project/python-dateutil/

.. |PyPI docopt| image:: https://img.shields.io/pypi/v/docopt.svg?style=flat-square
   :target: https://pypi.org/project/docopt/

.. |PyPI fs| image:: https://img.shields.io/pypi/v/fs.svg?style=flat-square
   :target: https://pypi.org/project/fs/

.. |PyPI fakeua| image:: https://img.shields.io/pypi/v/fake-useragent.svg?style=flat-square
   :target: https://pypi.org/project/fake-useragent/

.. |PyPI requests| image:: https://img.shields.io/pypi/v/requests.svg?style=flat-square
   :target: https://pypi.org/project/requests

.. |PyPI six| image:: https://img.shields.io/pypi/v/six.svg?style=flat-square
   :target: https://pypi.org/project/six

.. |PyPI tenacity| image:: https://img.shields.io/pypi/v/tenacity.svg?style=flat-square
   :target: https://pypi.org/project/tenacity

.. |PyPI tqdm| image:: https://img.shields.io/pypi/v/tqdm.svg?style=flat-square
   :target: https://pypi.org/project/tqdm

.. |PyPI verboselogs| image:: https://img.shields.io/pypi/v/verboselogs.svg?style=flat-square
   :target: https://pypi.org/project/verboselogs

.. |Source coloredlogs| image:: https://img.shields.io/badge/source-GitHub-303030.svg?style=flat-square
   :target: https://github.com/xolox/python-coloredlogs

.. |Source dateutil| image:: https://img.shields.io/badge/source-GitHub-303030.svg?style=flat-square
   :target: https://github.com/dateutil/dateutil/

.. |Source docopt| image:: https://img.shields.io/badge/source-GitHub-303030.svg?style=flat-square
   :target: https://github.com/docopt/docopt

.. |Source fs| image:: https://img.shields.io/badge/source-GitHub-303030.svg?style=flat-square
   :target: https://github.com/PyFilesystem/pyfilesystem2

.. |Source fakeua| image:: https://img.shields.io/badge/source-GitHub-303030.svg?style=flat-square
   :target: https://github.com/hellysmile/fake-useragent

.. |Source requests| image:: https://img.shields.io/badge/source-GitHub-303030.svg?style=flat-square
   :target: https://github.com/kennethreitz/requests

.. |Source six| image:: https://img.shields.io/badge/source-GitHub-303030.svg?style=flat-square
   :target: https://github.com/benjaminp/six

.. |Source tenacity| image:: https://img.shields.io/badge/source-GitHub-303030.svg?style=flat-square
   :target: https://github.com/jd/tenacity

.. |Source tqdm| image:: https://img.shields.io/badge/source-GitHub-303030.svg?style=flat-square
   :target: https://github.com/tqdm/tqdm

.. |Source verboselogs| image:: https://img.shields.io/badge/source-GitHub-303030.svg?style=flat-square
   :target: https://github.com/xolox/python-verboselogs

.. |License coloredlogs| image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
   :target: https://choosealicense.com/licenses/mit/

.. |License dateutil| image:: https://img.shields.io/pypi/l/python-dateutil.svg?style=flat-square
   :target: https://choosealicense.com/licenses/apache-2.0/

.. |License docopt| image:: https://img.shields.io/pypi/l/docopt.svg?style=flat-square
   :target: https://choosealicense.com/licenses/mit/

.. |License fs| image:: https://img.shields.io/pypi/l/fs.svg?style=flat-square
   :target: https://choosealicense.com/licenses/mit/

.. |License fakeua| image:: https://img.shields.io/badge/license-Apache_2.0-blue.svg?style=flat-square
   :target: https://choosealicense.com/licenses/apache-2.0/

.. |License requests| image:: https://img.shields.io/pypi/l/requests.svg?style=flat-square
   :target: https://choosealicense.com/licenses/apache-2.0/

.. |License six| image:: https://img.shields.io/pypi/l/six.svg?style=flat-square
   :target: https://choosealicense.com/licenses/mit/

.. |License tenacity| image:: https://img.shields.io/badge/license-Apache_2.0-blue.svg?style=flat-square
   :target: https://choosealicense.com/licenses/apache-2.0/

.. |License tqdm| image:: https://img.shields.io/pypi/l/tqdm.svg?style=flat-square
   :target: https://choosealicense.com/licenses/mpl-2.0/

.. |License verboselogs| image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
   :target: https://choosealicense.com/licenses/mit/


Installation
------------

InstaLooter is available on PyPI to install with ``pip``. If you are not
familiar with the package management of the Python ecosystem, please see the
`Installation page <http://instalooter.readthedocs.io/en/latest/install.html>`_
of the `documentation <http://instalooter.readthedocs.io/en/latest/index.html>`_.
Yet, you will probably end up using the following command::

  pip install --user instalooter --pre


Usage
-----

instalooter comes with its CLI::

    $ instalooter user <username> [<directory>] [options]
    $ instalooter hashtag <hashtag> [<directory>] [options]
    $ instalooter post <post_token> [<directory>] [options]
    $ instalooter batch [<batch_file>]

See ``instalooter --usage`` for all possible uses, or ``instalooter --help``
for a complete usage guide.


Logging in and out
------------------
There are two ways to login on Instagram through instalooter:

* use the *login* subcommand (``instalooter login``) to interactively login
  using your username and password.
* give a ``--username`` (and, if you want, a ``--password``) argument to any of
  the download commands.

In both cases, a session cookie will be created in a cache-specific folder.
To delete it and close your session on the server, use the ``logout``
subcommand.


Examples
--------

Download all **pictures** from the *instagram* profile in the current directory::

    $ instalooter user instagram

Download the latest 20 pictures or videos tagged with *python* to */tmp*::

    $ instalooter hashtag python /tmp -n 20 --get-videos -c MYLOGIN

Download a single post from an url in the `~/Pictures` directory::

    $ instalooter post "https://www.instagram.com/p/BFB6znLg5s1/" ~/Pictures

Use a configuration file to download from several account using custom parameters
(see `Batch mode <http://instalooter.readthedocs.io/en/latest/batch.html>`_)::

    $ instalooter batch /path/to/a/config/file.ini

See more on the `Usage page <http://instalooter.readthedocs.io/en/latest/usage.html>`_
of the `online documentation <http://instalooter.readthedocs.io/en/latest/index.html>`_.
