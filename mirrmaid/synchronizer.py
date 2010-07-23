# Copyright 2009, 2010 John Florian <jflorian@doubledog.org>
#
# This file is part of mirrmaid.
# 
# mirrmaid is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version so long as this copyright notice remains
# intact.
# 
# mirrmaid is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with mirrmaid.  If not, see <http://www.gnu.org/licenses/>.


__author__ = """John Florian <jflorian@doubledog.org>"""


from subprocess import PIPE, Popen, STDOUT
from time import strftime
import logging
import os

from doubledog.config import Config, Default_Config
from doubledog.lock import Lock_Exception, Lock_File


"""
This module implements a mirror synchronizer that is charged with maintaining a perfect target replica of a
source directory structure.  To ensure that only one synchronizer is working on a target replica at a time,
advisory locking is utilized.
"""


LOCK_DIRECTORY = "/var/lock/subsys/mirrmaid/"


class Synchronizer_Exception(Exception):
    pass


class Synchronizer(object):

    def __init__(self, default_conf, mirror_conf):
        """Construct a Synchronizer object that observes the default and mirror-specific configuration."""

        self.default_conf = default_conf
        self.mirror_conf = mirror_conf
        self.log = logging.getLogger("manager.synchronizer.%s" % self.mirror_conf.get_mirror_name())
        self.lock_file = Lock_File(self._get_lock_name(), pid=os.getpid())

    def _ensure_lock_directory_exists(self):
        """Make the lock directory unless it already exists."""
        try:
            if not os.path.isdir(LOCK_DIRECTORY):
                os.makedirs(LOCK_DIRECTORY)
        except OSError, e:
            raise Synchronizer_Exception("cannot create lock directory: %s" % e)

    def _get_lock_name(self):
        """Return the name of the lock file for the target replica."""

        return os.path.join(LOCK_DIRECTORY, self.mirror_conf.get_mirror_name())

    def _get_rsync_excludes(self):
        """Return the rsync options to effect the mirror's list of exclusions."""

        result = []
        for exclude in self.mirror_conf.get_excludes():
            result.append("--exclude")
            result.append(exclude)
        return result

    def _get_rsync_includes(self):
        """Return the rsync options to effect the mirror's list of inclusions."""

        result = []
        for include in self.mirror_conf.get_includes():
            result.append("--include")
            result.append(include)
        return result

    def _get_rsync_options(self):
        """Return the default rsync options to be used as a list."""

        return eval(self.default_conf.get("rsync_options"))

    def _get_source(self):
        """Return the fully-qualified rsync URI for the source of the directory structure to be mirrored."""

        source = self.mirror_conf.get_source()
        if not source.endswith('/'):
            source += "/"
        return source

    def _get_target(self):
        """Return the fully-qualified rsync URI for the target target of the mirroring operation."""

        target = self.mirror_conf.get_target()
        if not target.endswith('/'):
            target += "/"
        return target

    def _lock_replica(self):
        """Attempt to gain a lock on the target replica.

        Locks are per target so that multiple Synchronizers may be working concurrently so long as it is not
        on the same collection job.
        """

        self._ensure_lock_directory_exists()
        try:
            self.lock_file.exclusive_lock()
        except Lock_Exception:
            self.log.info("%s already locked by another process" % self.lock_file.get_name())
            return False
        else:
            self.log.info("gained exclusive-lock on %s" % self.lock_file.get_name())
            return True

    def _unlock_replica(self):
        """Release the lock on the target replica."""
        try:
            self.lock_file.unlock(delete_file=True)
            self.log.info("released exclusive-lock on %s" % self.lock_file.get_name())
        except OSError, e:
            self.log.error("failed to remove lock file: %s because:\n%s" % (self.lock_file.get_name()), e)

    def _update_replica(self):
        """Start an instance of rsync with the necessary options and arguments to effect a one-time
        synchronization.  Capture all stdout/stderr from the process and inject it into the logger.  The exit
        code of the rsync process is returned, where only a value of zero indicates success.
        """

        self.log.info("mirror synchronization started")
        cmd = ( ["/usr/bin/rsync"]
            + self._get_rsync_options()
            + self._get_rsync_includes()
            + self._get_rsync_excludes() )
        cmd.append(self._get_source())
        cmd.append(self._get_target())
        self.log.debug("spawning %s" % cmd)
        self.log.debug("AKA      %s" % " ".join(cmd))
        process = Popen(cmd, stdout=PIPE, stderr=STDOUT)
        self.log.info("rsync pid=%s" % process.pid)
        exit = None
        while True:
            output = process.stdout.readline()
            if process.poll():
                # note returncode, but continue reading to drain source
                exit = process.returncode
            if output == "":
                if exit is None:
                    exit = process.returncode
                if exit is not None:
                    if exit < 0:
                        self.log.warn("rsync terminated; caught signal %s" % -exit)
                    else:
                        level = [logging.INFO, logging.DEBUG][exit == os.EX_OK]
                        self.log.log(level, "rsync exit code=%s" % exit)
                    break
            else:
                self.log.info(output.rstrip())
        self.log.info("mirror synchronization finished")
        return exit

    def run(self):
        """Acquire a lock and if successful, update the target replica."""

        if self._lock_replica():
            try:
                self._update_replica()
            finally:
                self._unlock_replica()
