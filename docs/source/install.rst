Installation
============

.. toctree::

InstaLooter is available from 2 different sources: either a git repository,
shared publicly on GitHub, and a Python wheel, available on PyPI. Instructions
on how to setup each version are available below.

The python modules ``pip`` and ``setuptools`` are required before you start
installing InstaLooter. Although not strictly required, there will be no
explanations on how to setup instaLooter without those.

.. hint::

   See the `PyPA web page <https://pip.pypa.io/en/stable/installing/>`_
   page to install ``pip`` if it is not already installed.

.. attention::

    Using ``pip`` will install InstaLooter with the default Python version.
    InstaLooter is known to work with Python versions **2.7**, **3.4**
    and **3.5**, but encoding errors have been reported with Python **2.7**. If
    you are not familiar with the default Python version on you system, consider
    enforcing an installation with Python 3 using ``pip3`` instead of ``pip``.

PyPI |pypi|
-----------

If you have super user rights, open up a terminal and type the following:

.. code-block:: console

   # pip install instaLooter

If you don't have admin rights, then type the following to install only for
the current user instead:


.. code-block:: console

   $ pip install instaLooter --user


If you want to use the *exif* metadata features, install the ``metadata`` extras
as well:

.. code-block:: console

   $ pip install instaLooter[metadata] --user


GitHub |build|
--------------

With ``git`` installed, do the following in a directory on your machine to
clone the remote repository and install instaLooter from source:

.. code-block:: console

   $ git clone https://github.com/althonos/InstaLooter
   $ cd InstaLooter

Then use pip to install the local version of the program and all the required
dependencies:

.. code-block:: console

  # pip install .

To install development dependencies (to test the program and/or build the
documentation), use the *test* and/or *doc* extras:

.. code-block:: console

  $ pip install --user ".[test]"    # install only test dependencies
  $ pip install --user ".[doc]"     # install only doc dependencies
  $ pip install --user ".[dev]"     # install all dev dependencies


.. |pypi| image:: https://img.shields.io/pypi/v/instaLooter.svg?maxAge=3600&style=flat-square
   :target: https://pypi.org/project/instaLooter

.. |build| image:: https://img.shields.io/travis/althonos/InstaLooter/master.svg?label=travis-ci&maxAge=3600&style=flat-square
   :target: https://travis-ci.org/althonos/InstaLooter/
