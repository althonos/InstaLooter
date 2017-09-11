Periodic downloads
==================

``instaLooter`` may be used to update a local mirror of an instagram account,
and as such it may be desired to run it periodically, without needing to update
manually.

Linux & UNIX-like
-----------------

To support the UNIX philosophy, the program do not implement this feature itself
but should integrate well with established alternatives. The following examples
make use of either `Cron <https://en.wikipedia.org/wiki/Cron>`_ or
`SystemD timers <https://wiki.archlinux.org/index.php/Systemd/Timers>`_.

Cron
^^^^

First of all, make sure ``Cron`` is installed, and if not, refer to the
package manager of your distribution (if you're on MacOS, give a try to
`homebrew <https://brew.sh/>`_ if not using it already !).

Then, edit ``Cron`` to add a scheduled task::

  crontab -e

This will open a file using the **EDITOR** system variable to find a text
editor, such as *nano*, *pico*, *vi*, etc. Then, add a line as one of the
examples below to run instaLooter periodically:

* Download maximum 3 new ``#funny`` videos to ``~/Videos`` every hour::

    @hourly /usr/bin/env python -m instaLooter hashtag funny ~/Videos -N -n 3 -V

* Download new pictures w/ metadata from the ``instagram`` account at every reboot::

    @reboot /usr/bin/env python -m instaLooter instagram ~/Pictures/instagram -Nm

* Use a configuration file to download in :doc:`batch` every week on Sunday, 00:00 ::

    @weekly /usr/bin/env python -m instaLooter batch ~/myLooter.ini


Of course, ``Cron`` is extremely customisable, so if one of these do not fill
your needs, then head over to the `CronHowTo <https://help.ubuntu.com/community/CronHowto>`_.
