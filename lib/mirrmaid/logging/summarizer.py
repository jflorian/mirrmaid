# coding=utf-8

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2012-2020 John Florian <jflorian@doubledog.org>
#
# This file is part of mirrmaid.


"""
This module implements a mirror summarizer for the purpose of keeping one or
more people informed of the current mirror state.
"""
import errno
import logging.handlers
import shelve
import sys
from hashlib import md5
from logging import LogRecord
from socket import getfqdn
from time import asctime, ctime, time
from typing import Optional

from doubledog.mail import MiniMailer

from mirrmaid.constants import *

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2012-2020 John Florian"""


class SummaryGroup(object):
    def __init__(self, name):
        self.name = name
        self.hash = md5(name.encode()).hexdigest()


class LogState(object):
    """A trivial, persistent shelf object for recording log rotation state."""

    GROUP_TAG = 'group_tag'
    LAST_ROLLOVER = 'last_rollover'

    def __init__(self, summary_group):
        self.summary_group = summary_group
        self.filename = self.__log_state_filename()
        # Establish initial conditions such that it appears a log rollover has
        # just occurred, since that best matches the actual case of having an
        # emtpy log.  This ensures a rollover will occur in
        if self.last_rollover is None:
            self.last_rollover = time()

    def __log_state_filename(self):
        return f'{LOG_STATE}.{self.summary_group.hash}'

    @property
    def last_rollover(self) -> Optional[float]:
        """
        :return:
            The number of seconds since the last rollover.
        """
        shelf = None
        try:
            shelf = shelve.open(self.filename)
            return shelf[self.LAST_ROLLOVER]
        except KeyError:
            return None
        finally:
            if shelf:
                shelf.close()

    @last_rollover.setter
    def last_rollover(self, when: float):
        """
        Record the time of rollover.

        :param when:
            The time when the rollover occurred.
        """
        shelf = None
        try:
            shelf = shelve.open(self.filename)
            shelf[self.GROUP_TAG] = self.summary_group.name
            shelf[self.LAST_ROLLOVER] = when
        finally:
            if shelf:
                shelf.close()


# noinspection PyPep8Naming
class LogSummarizingHandler(logging.handlers.RotatingFileHandler):
    """
    This class extends the RotatingFileHandler with an additional rollover
    trigger based on the elapsed time since the last rollover.  Thus this
    handler ensure the log gets a rollover whenever maxBytes is exceeded or
    when the elapsed time exceeds the configured summary_interval, whichever
    occurs first.

    When a rollover does occur, the log content just displaced will be
    delivered via email as a means of summarizing the important messages that
    had occurred during this most recent summary interval.
    """

    def __init__(self, mirrmaid_config):
        self.mirrmaid_config = mirrmaid_config
        self.summary_group = SummaryGroup(self.mirrmaid_config.summary_group)
        self._log_state = LogState(self.summary_group)
        self._reset_reasons()
        super().__init__(
            self.__log_filename,
            maxBytes=self.mirrmaid_config.summary_size,
            backupCount=self.mirrmaid_config.summary_history_count
        )

    @property
    def __log_filename(self):
        return f'{SUMMARY_FILENAME}.{self.summary_group.hash}'

    @property
    def __subject(self):
        return (f'mirrmaid Activity Summary for '
                f'{self.mirrmaid_config.summary_group}')

    @property
    def _reason(self) -> str:
        """
        :return:
            Formatted message stating reason(s) for rollover.
        """
        reasons = []
        if self._rolled_for_age:
            reasons.append('age')
        if self._rolled_for_size:
            reasons.append('size')
        if len(reasons):
            return f'{" and ".join(reasons)} of logged messages'
        else:
            return 'forced'

    @property
    def _summary_body(self):
        since = ctime(self._log_state.last_rollover)
        until = asctime()
        with open(f'{self.baseFilename}.1') as f:
            log_content = f.read()
        body = [
            f'{"Since":>25}:  {since}',
            f'{"Until":>25}:  {until}',
            f'{"Reason for Notification":>25}:  {self._reason}',
            '\n',
        ]
        if log_content.strip() == '':
            body.append('STATUS GOOD!  No warnings or errors to summarize.')
        else:
            body.append('=== Start of Warning/Error Summary ===')
            body.append(log_content)
            body.append('=== End of Warning/Error Summary ===')
        return '\n'.join(body)

    @property
    def summary_due(self) -> bool:
        """
        Determine if a summary is needed based on age.

        :return:
            ``True`` iff logged messages are sufficiently aged.
        """
        age = time() - self._log_state.last_rollover
        due = age > self.mirrmaid_config.summary_interval
        # Class state is for summary body, which is cumulative via boolean OR.
        # Method return value must remain distinct as to what is true right now
        # whereas the class state is what has been true since last
        # notification.
        self._rolled_for_age |= due
        return due

    def _mail_summary(self):
        sender = f'mirrmaid@{getfqdn()}'
        try:
            MiniMailer().send(
                sender,
                self.mirrmaid_config.summary_recipients,
                self.__subject,
                self._summary_body
            )
        except ConnectionError as e:
            sys.stderr.write(f'Unable to mail log summary: {e}\n')
        self._reset_reasons()

    def _reset_reasons(self):
        self._rolled_for_age = False
        self._rolled_for_size = False

    def doRollover(self):
        """
        Overridden method.  Perform all inherited behavior and mail any content
        just rolled out of the current log file.
        """
        try:
            super().doRollover()
        except FileNotFoundError:
            # http://bugs.python.org/issue18940 was resolved poorly by
            # introducing a race condition, but perhaps the RotatingFileHandler
            # wasn't intended for multi-process access to the same log target.
            # If the source is missing, we can assume that another process has
            # already performed the rollover.
            pass
        self._mail_summary()
        self._log_state.last_rollover = time()

    def force_rollover(self):
        # There may not be any log file on which to perform the rollover.  The
        # important thing is to issue the summary and reset the last rollover
        # time.
        try:
            self.doRollover()
        except (IOError, OSError) as e:
            if e.errno != errno.ENOENT:
                raise

    def shouldRollover(self, record: LogRecord) -> bool:
        """
        Determine if a rollover is needed.

        A rollover is needed whenever:
            1. the log attains a certain minimum size
            2. the log contains content that has attained a certain minimum age

        :param record:
            Log record about to be committed.

        :return:
            ``True`` iff a rollover is needed for any reason.
        """
        for_size = super().shouldRollover(record)
        for_age = self.summary_due
        # Class state is for summary body, which is cumulative via boolean OR.
        # Method return value must remain distinct as to what is true right now
        # whereas the class state is what has been true since last
        # notification.
        self._rolled_for_size |= for_size
        return for_age or for_size
