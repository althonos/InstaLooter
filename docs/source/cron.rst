Periodic downloads
==================

``instaLooter`` may be used to update a local mirror of an instagram account,
and as such it may be desired to run it periodically, without needing to update
manually.



UNIX
----

To support the UNIX philosophy, the program do not implement this feature itself
but should integrate well with established alternatives. The following examples
make use of either `Cron <https://en.wikipedia.org/wiki/Cron>`_ or
`SystemD timers <https://wiki.archlinux.org/index.php/Systemd/Timers>`_.


Cron
^^^^
First of all, make sure ``Cron`` is installed, and if not, refer to the
package manager of your distribution (if you're on MacOS, give a try to
`homebrew <https://brew.sh/>`_ if not using it already !).

Then, edit ``Cron`` to add a scheduled task:

.. code-block:: console

  $ crontab -e

This will open a file using the **$EDITOR** system variable to find a text
editor, such as *nano*, *pico*, *vi*, etc. Then, add one line as one of the
examples below to run instaLooter periodically (you can add more than one line
if you have more than one goal in mind):

* Download maximum 3 new ``#funny`` videos to ``~/Videos`` every hour::

    @hourly /usr/bin/env python -m instaLooter hashtag funny ~/Videos -N -n 3 -V

* Download new pictures w/ metadata from the ``instagram`` account at every reboot::

    @reboot /usr/bin/env python -m instaLooter instagram ~/Pictures/instagram -Nm

* Use a configuration file to download in :doc:`batch` every week on Sunday, 00:00 ::

    @weekly /usr/bin/env python -m instaLooter batch ~/myLooter.ini


To disable a scheduled task, simply remove the line associated to that task within
*crontab*.

.. seealso::

    * The `CronHowTo <https://help.ubuntu.com/community/CronHowto>`_ hosted
      on *ubuntu.org* for a complete understanding of the crontab line format.

SystemD
^^^^^^^
You'll probably use this alternative if your system is already running on top of
SystemD. If not, you should probably turn to ``Cron``. Simply check for the
existence of a ``systemctl`` executable (e.g. running ``systemctl --help``) to
see if you're using SystemD.

Create a new service file, either in ``/etc/systemd/system/`` for system-wide jobs,
or in ``~/.config/systemd/user/`` for user-only jobs, named for instance
``looter.service`` (you can use any name as long as the file has a *.service*
extension), with the following content:

.. code-block:: ini

  [Unit]
  Description=my custom periodic instagram looter

  [Service]
  Type=oneshot
  ExecStart=/usr/bin/env python -m instaLooter <the parameters I want>

Make sure the ``instaLooter`` module is accessible to the ``systemd`` manager,
i.e. if you're using system-wide jobs that the module was installed in */usr* (not
with ``pip insta --user instaLooter`` but with ``pip install instaLooter``).

To test your service, run ``systemctl start looter.service`` (using the name of
your file), or ``systemctl --user start looter.service`` if you want to use
user-only jobs. There should be no output if everything works fine.

If a bug occurs check the logs with *journalctl*:

.. code-block:: console

    # journalctl looter.service
    $ journalctl --user --user-unit looter.service

Once your service works fine, create a timer for your new service, named like
and located next to your service file, but with a ``.timer`` extension, and
the following content:

.. code-block:: ini

  [Unit]
  Description=run my custom periodic instagram looter hourly

  [Timer]
  # Time to wait after booting before we run first time
  OnBootSec=10min
  # Time between running each consecutive time
  OnUnitActiveSec=1h
  Unit=looter.service

Finally, enable and start your timer with one of the following commands:

.. code-block:: console

    # systemctl start looter.timer && systemctl enable looter.timer
    $ systemctl --user start looter.timer && systemctl --user enable looter.timer

To disable the timer, use the same command as above, replacing ``start`` with
``stop`` and ``enable`` by ``disable``, and remove the service and timer files
if you want to completely uninstall the timer.

.. seealso::

    * The `SystemD/timers <https://wiki.archlinux.org/index.php/Systemd/Timers>`_
      and the whole `SystemD <https://wiki.archlinux.org/index.php/Systemd>`_
      pages on the *Archlinux wiki* for more details about timer and services.
    * The `post on Jason's blog <https://jason.the-graham.com/2013/03/06/how-to-use-systemd-timers/>`_
      that helped shaping this tutorial.
