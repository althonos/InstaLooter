Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <http://keepachangelog.com>`_ and this
project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_.

Unreleased_
-----------

v2.4.2_ - 2019-12-27
--------------------

Changed
'''''''
- CLI `--time` option will now always use higher and lower time given as the 
  timeframe, independently of the order they are given.

Fixed
'''''
- JSON files also get a proper timestamp set (pr #275).


v2.4.1_ - 2019-12-10
--------------------

Fixed
'''''
- Issue with additional data not being loaded from certain pages (#271) (pr #273)


v2.4.0_ - 2019-06-29
--------------------

Fixed
'''''
- Attempt fix for `rhx_gis` issue (#247) (pr #248)
- Fix crashes when downloading hashtag medias

Changed
'''''''
- Removed ``fake-useragent`` dependency.
- Use a custom HTTP server to detect the user agent of the default web browser.

v2.3.4_ - 2019-02-22
--------------------

Fixed
'''''
- Bumped supported ``fs`` version to ``~=2.1``.

v2.3.3_ - 2019-02-11
--------------------

Fixed
'''''
- Bumped supported ``fs`` version to ``2.3.0``.

v2.3.2_ - 2019-01-06
---------------------

Added
'''''
- Add zero padding for date and time in filenames (pr #224)

Changed
'''''''
- Add `tests` to source distribution (pr #228).
- Bumped supported ``fs`` version to ``2.2.0``.

v2.3.1_ - 2018-10-13
--------------------

Fixed
'''''
- Allow extracting post codes of length 10 from URLs.


v2.3.0_ - 2018-09-05
--------------------

Changed
'''''''
- Bumped required ``tenacity`` version to ``5.0``.

v2.2.0_ - 2018-08-19
--------------------

Changed
'''''''
- Bumped required ``fs`` version to ``2.1.0``.


v2.1.0_ - 2018-07-31
--------------------

Added
'''''
- Posts can now be downloaded by giving directly the post URL (implement #184).

Fixed
'''''
- Batch will now log the name of the current account as well as occuring
  errors (fix #185)
- CLI login will now properly display logger messages.
- Library loggers do not have a `logging.StreamHandler` set by default
  anymore.
- Attempt fixing login procedure in ``InstaLooter._login``.

Changed
'''''''
- Trying to download media from an non-existing user will display a nicer
  message: ``user not found: '...'`` (fix #194).
- Batch mode will now continue to the next job if any error occurs, showing
  an error message instead of crashing (fix #185).


v2.0.3_ - 2018-05-29
--------------------

Fixed
'''''
- Use the webpage shared data to find the CSRF token instead of response
  cookies.

v2.0.2_ - 2018-05-17
--------------------

Changed
'''''''
- Bump ``coloredlogs`` required version to `10.0`.
- Use ``verboselogs`` as the backend logging library.


v2.0.1_ - 2018-04-18
--------------------

Changed
'''''''
- Updated the query hash in ``ProfileIterator`` (although previous seemed
  to keep working).

Fixed
'''''
- *RHX-GIS* computation not using the CSRF token anymore.
- Lowered ``PageIterator.PAGE_SIZE`` to 50 to comply with Instagram.


v2.0.0_ - 2018-04-16
--------------------

Changed
'''''''
- Passing a pre-initialised ``Session`` to ``PageIterator`` constructor
  is now mandatory.
- ``HashtagIterator`` must be provided a ``rhx`` (it is infered for ``ProfileIterator``).

Fixed
'''''
- API changes made by Instagram ca. April 2018 (excluding logging in / out).
- Calling `operator.length_hint` on ``PageIterator`` objects will no longer
  cause duplicate server queries.


v1.0.0_ - 2018-04-05
--------------------

Added
'''''
- This CHANGELOG file.
- Typing annotations using the ``typing`` module.
- Limited retries on connection failure, using `tenacity <https://http://pypi.org/project/tenacity/>`_.
- Real-world User Agent spoofing, using `fake-useragent <https://pypi.org/project/fake-useragent/>`_

Fixed
'''''
- API changes made by Instagram ca. March 2018.

Changed
'''''''
- Whole new API following major code refactor and rewrite.
- Requests to the API directly use JSON and GraphQL queries when possible.
- License is now GPLv3 *or later* instead of GPLv3.
- I/O now uses PyFilesystem (FS URLs can be passed as CLI arguments).

Removed
'''''''
- Exif metadata handling (*will be added back in later release*).
- ``urlgen`` capabilities (Instagram signs picture URL since 2018).
- Python 3.5.1 support (lacks the required ``typing`` version).
- ``progressbar2`` dependency, replaced by ``tqdm``
- ``hues`` dependency, replaced by ``coloredlogs``
- ``BeautifulSoup4`` dependency

.. _Unreleased: https://github.com/althonos/InstaLooter/compare/v2.4.0...HEAD
.. _v2.4.0: https://github.com/althonos/InstaLooter/compare/v2.3.4...v2.4.0
.. _v2.3.4: https://github.com/althonos/InstaLooter/compare/v2.3.3...v2.3.4
.. _v2.3.3: https://github.com/althonos/InstaLooter/compare/v2.3.2...v2.3.3
.. _v2.3.2: https://github.com/althonos/InstaLooter/compare/v2.3.1...v2.3.2
.. _v2.3.1: https://github.com/althonos/InstaLooter/compare/v2.3.0...v2.3.1
.. _v2.3.0: https://github.com/althonos/InstaLooter/compare/v2.2.0...v2.3.0
.. _v2.2.0: https://github.com/althonos/InstaLooter/compare/v2.1.0...v2.2.0
.. _v2.1.0: https://github.com/althonos/InstaLooter/compare/v2.0.3...v2.1.0
.. _v2.0.3: https://github.com/althonos/InstaLooter/compare/v2.0.2...v2.0.3
.. _v2.0.2: https://github.com/althonos/InstaLooter/compare/v2.0.1...v2.0.2
.. _v2.0.1: https://github.com/althonos/InstaLooter/compare/v2.0.0...v2.0.1
.. _v2.0.0: https://github.com/althonos/InstaLooter/compare/v1.0.0...v2.0.0
.. _v1.0.0: https://github.com/althonos/InstaLooter/compare/v0.14.0...v1.0.0
