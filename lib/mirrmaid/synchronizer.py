# coding=utf-8
# Copyright 2009-2016 John Florian <jflorian@doubledog.org>
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

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2009-2016 John Florian"""


class Synchronizer(object):
    """
    This is effectively a Python wrapper around the venerable rsync, but made
    suitable for mirrmaid use.  The options and arguments for rsync are mostly
    derived from the mirrmaid configuration file.  A Synchronizer object works
    on a single mirror.  Multiple Synchronizers may run concurrently provided
    they are operating on distinct mirrors.  This is enforced via lock-files
    on a per-mirror basis.
    """

    def __init__(self, default_conf, mirror_conf):
        """
        Initialize the Synchronizer object.

        This will happen according to the default and mirror-specific
        sections of the configuration file..
        """
        self.default_conf = default_conf
        self.mirror_conf = mirror_conf
        self.log = logging.getLogger(
            'mirrmaid.{0}'.format(self.mirror_conf.mirror_name)
        )
        self.lock_file = LockFile(self._lock_name, pid=os.getpid())

    @property
    def _lock_name(self) -> str:
        """
        :return:
            The name of the lock-file for the target replica.
        """
        return os.path.join(LOCK_DIRECTORY, self.mirror_conf.mirror_name)

    @property
    def _rsync_excludes(self) -> list:
        """
        :return:
            The rsync options to effect the mirror's list of exclusions.
        """
        result = []
        for exclude in self.mirror_conf.excludes:
            result.append('--exclude')
            result.append(exclude)
        return result

    @property
    def _rsync_includes(self) -> list:
        """
        :return:
            The rsync options to effect the mirror's list of inclusions.
        """
        result = []
        for include in self.mirror_conf.includes:
            result.append('--include')
            result.append(include)
        return result

    @property
    def _rsync_options(self) -> list:
        """
        :return:
            The default rsync options to be used.
        """
        return self.default_conf.get_list('rsync_options')

    @property
    def _source(self) -> str:
        """
        :return:
            The fully-qualified rsync URI for the source of the directory
            structure to be mirrored.
        """
        source = self.mirror_conf.source
        if not source.endswith('/'):
            source += '/'
        return source

    @property
    def _target(self) -> str:
        """
        :return:
            The fully-qualified rsync URI for the target target of the mirroring
            operation.
        """
        target = self.mirror_conf.target
        if not target.endswith('/'):
            target += '/'
        return target

    def _lock_replica(self) -> bool:
        """
        Attempt to gain a lock on the target replica.

        Locks are per target so that multiple Synchronizers may be working
        concurrently so long as it is not on the same collection job.

        :return:
            ``True`` iff the lock was gained.
        """
        try:
            self.lock_file.exclusive_lock()
        except LockException:
            self.log.info(
                '{!r} already locked by another process'.format(
                    self.lock_file.name,
                )
            )
            return False
        else:
            self.log.info(
                'gained exclusive-lock on {!r}'.format(
                    self.lock_file.name,
                )
            )
            return True

    def _unlock_replica(self):
        """Release the lock on the target replica."""
        try:
            self.lock_file.unlock(delete_file=True)
            self.log.info(
                'released exclusive-lock on {!r}'.format(self.lock_file.name)
            )
        except OSError as e:
            self.log.error(
                'failed to remove lock-file: {!r} because:\n{}'.format(
                    self.lock_file.name,
                    e,
                )
            )

    def _update_replica(self) -> int:
        """
        Effect a one-time synchronization.

        Start an instance of rsync with the necessary options and arguments,
        capturing all stdout/stderr from the process and inject it into the
        logger.

        :return:
            The exit code of the rsync process, where only a value of zero
            indicates success.
        """
        self.log.info('mirror synchronization started')
        cmd = (
            ['/usr/bin/rsync']
            + self._rsync_options
            + self._rsync_includes
            + self._rsync_excludes
        )
        cmd.append(self._source)
        cmd.append(self._target)
        self.log.debug('spawning {!r}'.format(cmd))
        self.log.debug('AKA      {0}'.format(' '.join(cmd)))
        process = AsynchronousStreamingSubprocess(cmd)
        self.log.info('rsync pid={!r}'.format(process.pid))
        exit_code = process.collect(self.log.info, self.log.error)
        if exit_code < 0:
            self.log.warn(
                'rsync terminated; caught signal {!r}'.format(-exit_code)
            )
        else:
            level = [logging.INFO, logging.DEBUG][exit_code == os.EX_OK]
            self.log.log(level, 'rsync exit code={!r}'.format(exit_code))
        self.log.info('mirror synchronization finished')
        return exit_code

    def run(self):
        """Acquire a lock and if successful, update the target replica."""
        if self._lock_replica():
            try:
                self._update_replica()
            finally:
                self._unlock_replica()
