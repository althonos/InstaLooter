#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function

import os
import sys
import functools
import warnings
import datetime
import dateutil.relativedelta
import hues

console = hues.SimpleConsole(stdout=sys.stderr)


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
        if not os.path.isdir(os.path.dirname(session.cookies.filename)):
            os.mkdir(os.path.dirname(session.cookies.filename))
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


def get_times(timeframe):
    """Get absolute times from a maybe incomplete timeframe.

    Argument:
        timeframe (`tuple`): a couple of `datetime.date` objects
            or eventually ``None``.

    Returns:
        tuple: a tuple with absolute `datetime.date` values (start ``None``
            is replaced with ``datetime.date.today()``, and end ``None``
            is replaced with ``datetime.date.fromtimestamp(0)``, i.e. the
            epoch).

    Raises:
        TypeError: If the provided object is not a sequence of (at least)
            two arguments.
    """
    if timeframe is None:
        timeframe = (None, None)
    try:
        start_time = timeframe[0] or datetime.date.today()
        end_time = timeframe[1] or datetime.date.fromtimestamp(0)
    except (IndexError, AttributeError):
        raise TypeError("'timeframe' must be a tuple of dates !")
    return start_time, end_time


def get_times_from_cli(cli_token):
    """Convert a CLI token to a datetime tuple.

    Argument:
        cli_token (`str`): an isoformat datetime token ([ISO date]:[ISO date])
            or a special value among:
                * thisday
                * thisweek
                * thismonth
                * thisyear

    Returns:
        tuple: a datetime.date objects couple, where the first item is
            the start of a time frame and the second item the end of the
            time frame. Both elements can also be None, if no date was
            provided.

    Raises:
        ValueError: when the CLI token is not in the right format
            (no colon in the token, not one of the special values, dates
            are not in proper ISO-8601 format.)

    See also:
        `ISO-8601 specification <https://en.wikipedia.org/wiki/ISO_8601>`_.
    """

    today = datetime.date.today()

    if cli_token=="thisday":
        return today, today
    elif cli_token=="thisweek":
        return today, today - dateutil.relativedelta.relativedelta(days=7)
    elif cli_token=="thismonth":
        return today, today - dateutil.relativedelta.relativedelta(months=1)
    elif cli_token=="thisyear":
        return today, today - dateutil.relativedelta.relativedelta(years=1)
    else:
        try:
            start_date, stop_date = cli_token.split(':')
        except ValueError:
            raise ValueError("--time parameter must contain a colon (:)")
        if not start_date and not stop_date: # ':', no start date, no stop date
            return None, None
        try:
            start_date = date_from_isoformat(start_date) if start_date else None #datetime.date.today()
            stop_date = date_from_isoformat(stop_date) if stop_date else None #datetime.date.fromtimestamp(0)
        except ValueError:
            raise ValueError("--time parameter was not provided ISO formatted dates")
        return start_date, stop_date


def date_from_isoformat(isoformat_date):
    """Convert an ISO-8601 date into a `datetime.date` object.

    Argument:
        isoformat_date (`string`): a date in ISO-8601 format
            (YYYY-MM-DD)

    Returns:
        `datetime.date`: the date object corresponding to the given ISO
            formatted date.

    Raises:
        ValueError: when the date could not be converted successfully.

    See also:
        `ISO-8601 specification <https://en.wikipedia.org/wiki/ISO_8601>`_.
    """
    year, month, day = isoformat_date.split('-')
    return datetime.date(int(year), int(month), int(day))


def warn_with_hues(message, category, filename, lineno, file=None, line=None):
    """Use `hues` to log warnings.
    """
    console.warn(message)

def warn_windows(message, category, filename, lineno, file=None, line=None):
    """Use a `hues`-like format to log warnings without color.
    """
    print(("{d.hour}:{d.minute}:{d.second} - WARNING - "
          "{msg}").format(d=datetime.datetime.now(), msg=message), file=sys.stderr)

def wrap_warnings(func):
    """Have the function patch `warnings.showwarning` when it is called.
    """
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        showwarning = warnings.showwarning
        if os.name == 'posix':
            warnings.showwarning = warn_with_hues
        else:
            warnings.showwarning = warn_windows
        result = func(*args, **kwargs)
        warnings.showwarning = showwarning
        return result
    return new_func
