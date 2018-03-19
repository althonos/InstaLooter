# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

__all__ = ["save_cookies", "load_cookies"]


def save_cookies(session):
    """Save cookies from a session.

    Arguments:
        session (`requests.Session`): a session with cookies
            to save.

    Note:
        Cookies are saved in a plain text file in the system
        system temporary directory. Use ``tempfile.gettempdir()``
        to find where it is.
    """
    try:
        session.cookies.save()
    except IOError:
        pass


def load_cookies(session):
    """Load saved cookies to a session.

    Arguments:
        session (`requests.session`): a session with saved
            cookies to load.

    Note:
        Expired cookies are cleaned, so the session will
        only load active cookies.
    """
    try:
        session.cookies.load()
    except IOError:
        pass
    session.cookies.clear_expired_cookies()
