# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import datetime

import dateutil.relativedelta


def date_from_isoformat(isoformat_date):
    """Convert an ISO-8601 date into a `datetime.date` object.

    Argument:
        isoformat_date (str): a date in ISO-8601 format (YYYY-MM-DD)

    Returns:
        ~datetime.date: the object corresponding to the given ISO date.

    Raises:
        ValueError: when the date could not be converted successfully.

    See Also:
        `ISO-8601 specification <https://en.wikipedia.org/wiki/ISO_8601>`_.
    """
    year, month, day = isoformat_date.split('-')
    return datetime.date(int(year), int(month), int(day))


def get_times_from_cli(cli_token):
    """Convert a CLI token to a datetime tuple.

    Argument:
        cli_token (str): an isoformat datetime token ([ISO date]:[ISO date])
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

    See Also:
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
            start_date = date_from_isoformat(start_date) if start_date else None
            stop_date = date_from_isoformat(stop_date) if stop_date else None
        except ValueError:
            raise ValueError("--time parameter was not provided ISO formatted dates")
        if start_date is not None and stop_date is not None:
            return max(start_date, stop_date), min(start_date, stop_date)
        else:
            return stop_date, start_date
