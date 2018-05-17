Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <http://keepachangelog.com>`_ and this
project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_.

Unreleased_
-----------

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

.. _Unreleased: https://github.com/althonos/InstaLooter/compare/v2.0.2...HEAD
.. _v2.0.2: https://github.com/althonos/InstaLooter/compare/v2.0.1...v2.0.2
.. _v2.0.1: https://github.com/althonos/InstaLooter/compare/v2.0.0...v2.0.1
.. _v2.0.0: https://github.com/althonos/InstaLooter/compare/v1.0.0...v2.0.0
.. _v1.0.0: https://github.com/althonos/InstaLooter/compare/v0.14.0...v1.0.0
