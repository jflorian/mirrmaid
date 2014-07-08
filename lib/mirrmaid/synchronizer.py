# Copyright 2009-2014 John Florian <jflorian@doubledog.org>
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


"""
This module implements a mirror synchronizer that is charged with maintaining
a perfect target replica of a source directory structure.  To ensure that only
one synchronizer is working on a target replica at a time, advisory locking is
utilized.
"""
import logging
import os

from doubledog.async import AsynchronousStreamingSubprocess
from doubledog.lock import LockException, LockFile

from mirrmaid.constants import *
from mirrmaid.exceptions import SynchronizerException


__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2009-2014 John Florian"""


class Synchronizer(object):
    def __init__(self, default_conf, mirror_conf):
        """Construct a Synchronizer object that observes the default and
        mirror-specific configuration.
        """

        self.default_conf = default_conf
        self.mirror_conf = mirror_conf
        self.log = logging.getLogger(
            'mirrmaid.{0}'.format(self.mirror_conf.mirror_name))
        self.lock_file = LockFile(self._get_lock_name(), pid=os.getpid())

    @staticmethod
    def _ensure_lock_directory_exists():
        """Make the lock directory unless it already exists."""
        try:
            if not os.path.isdir(LOCK_DIRECTORY):
                os.makedirs(LOCK_DIRECTORY)
        except OSError as e:
            raise SynchronizerException(
                'cannot create lock directory: {0}'.format(e))

    def _get_lock_name(self):
        """Return the name of the lock file for the target replica."""

        return os.path.join(LOCK_DIRECTORY, self.mirror_conf.mirror_name)

    def _get_rsync_excludes(self):
        """Return the rsync options to effect the mirror's list of exclusions.
        """

        result = []
        for exclude in self.mirror_conf.excludes:
            result.append('--exclude')
            result.append(exclude)
        return result

    def _get_rsync_includes(self):
        """Return the rsync options to effect the mirror's list of inclusions.
        """

        result = []
        for include in self.mirror_conf.includes:
            result.append('--include')
            result.append(include)
        return result

    def _get_rsync_options(self):
        """Return the default rsync options to be used as a list."""

        return self.default_conf.get_list('rsync_options')

    def _get_source(self):
        """Return the fully-qualified rsync URI for the source of the
        directory structure to be mirrored.
        """

        source = self.mirror_conf.source
        if not source.endswith('/'):
            source += '/'
        return source

    def _get_target(self):
        """Return the fully-qualified rsync URI for the target target of the
        mirroring operation.
        """

        target = self.mirror_conf.target
        if not target.endswith('/'):
            target += '/'
        return target

    def _lock_replica(self):
        """Attempt to gain a lock on the target replica.

        Locks are per target so that multiple Synchronizers may be working
        concurrently so long as it is not on the same collection job.
        """

        self._ensure_lock_directory_exists()
        try:
            self.lock_file.exclusive_lock()
        except LockException:
            self.log.info('{0} already locked by another process'.format(
                self.lock_file.name))
            return False
        else:
            self.log.info(
                'gained exclusive-lock on {0}'.format(self.lock_file.name))
            return True

    def _unlock_replica(self):
        """Release the lock on the target replica."""
        try:
            self.lock_file.unlock(delete_file=True)
            self.log.info(
                'released exclusive-lock on {0}'.format(self.lock_file.name))
        except OSError as e:
            self.log.error(
                'failed to remove lock file: {0} because:\n{1}'.format(
                    self.lock_file.name), e)

    def _update_replica(self):
        """Start an instance of rsync with the necessary options and arguments
        to effect a one-time synchronization.  Capture all stdout/stderr from
        the process and inject it into the logger.  The exit code of the rsync
        process is returned, where only a value of zero indicates success.
        """

        self.log.info('mirror synchronization started')
        cmd = ( ['/usr/bin/rsync']
                + self._get_rsync_options()
                + self._get_rsync_includes()
                + self._get_rsync_excludes() )
        cmd.append(self._get_source())
        cmd.append(self._get_target())
        self.log.debug('spawning {0}'.format(cmd))
        self.log.debug('AKA      {0}'.format(' '.join(cmd)))
        process = AsynchronousStreamingSubprocess(cmd)
        self.log.info('rsync pid={0}'.format(process.pid))
        exit = process.collect(self.log.info, self.log.error)
        if exit < 0:
            self.log.warn('rsync terminated; caught signal {0}'.format(-exit))
        else:
            level = [logging.INFO, logging.DEBUG][exit == os.EX_OK]
            self.log.log(level, 'rsync exit code={0}'.format(exit))
        self.log.info('mirror synchronization finished')
        return exit

    def run(self):
        """Acquire a lock and if successful, update the target replica."""

        if self._lock_replica():
            try:
                self._update_replica()
            finally:
                self._unlock_replica()
