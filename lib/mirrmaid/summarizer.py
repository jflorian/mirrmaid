# coding=utf-8
# Copyright 2012-2016 John Florian <jflorian@doubledog.org>
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
This module implements a mirror summarizer for the purpose of keeping one or
more people informed of the current mirror state.
"""
import errno
import logging.handlers
import shelve
import sys
from hashlib import md5
from socket import getfqdn
from time import time, ctime, asctime

from doubledog.mail import MiniMailer

from mirrmaid.constants import *

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2012-2016 John Florian"""


class SummaryGroup(object):
    def __init__(self, name):
        self.name = name
        self.hash = self.hash_name(self.name)

    @staticmethod
    def hash_name(name):
        return md5(name.encode()).hexdigest()


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
        return '{0}.{1}'.format(LOG_STATE, self.summary_group.hash)

    @property
    def last_rollover(self):
        """
        @return:    The number of seconds since the last rollover.
        @rtype:     float
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
    def last_rollover(self, when):
        """
        Record the time of rollover.

        @param when:    The time when the rollover occurred.
        @type when:     float
        """

        shelf = None
        try:
            shelf = shelve.open(self.filename)
            shelf[self.GROUP_TAG] = self.summary_group.name
            shelf[self.LAST_ROLLOVER] = when
        finally:
            if shelf:
                shelf.close()


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
        super(LogSummarizingHandler, self).__init__(
            self.__log_filename,
            maxBytes=self.mirrmaid_config.summary_size,
            backupCount=self.mirrmaid_config.summary_history_count
        )

    @property
    def __log_filename(self):
        return '{0}.{1}'.format(SUMMARY_FILENAME, self.summary_group.hash)

    @property
    def __subject(self):
        return 'mirrmaid Activity Summary for {0}'.format(
            self.mirrmaid_config.summary_group)

    def _mail_summary(self):
        sender = 'mirrmaid@{0}'.format(getfqdn())
        try:
            MiniMailer().send(
                sender,
                self.mirrmaid_config.summary_recipients,
                self.__subject,
                self._summary_body()
            )
        except ConnectionError as e:
            sys.stderr.write('Unable to mail log summary: {}\n'.format(e))
        self._reset_reasons()

    def _reason(self):
        """
        @return:    Formatted message stating reason(s) for rollover.
        @rtype:     str
        """
        reasons = []
        if self._rolled_for_age:
            reasons.append('age')
        if self._rolled_for_size:
            reasons.append('size')
        if len(reasons):
            return '{0} of logged messages'.format(' and '.join(reasons))
        else:
            return 'forced'

    def _reset_reasons(self):
        self._rolled_for_age = False
        self._rolled_for_size = False

    def _summary_body(self):
        since = ctime(self._log_state.last_rollover)
        until = asctime()
        with open('{0}.1'.format(self.baseFilename)) as f:
            log_content = f.read()
        heading = '{0:>25}:  {1}'
        body = [
            heading.format('Since', since),
            heading.format('Until', until),
            heading.format('Reason for Notification', self._reason()),
            '\n',
        ]
        if log_content.strip() == '':
            body.append('STATUS GOOD!  No warnings or errors to summarize.')
        else:
            body.append('=== Start of Warning/Error Summary ===')
            body.append(log_content)
            body.append('=== End of Warning/Error Summary ===')
        return '\n'.join(body)

    def doRollover(self):
        """
        Overridden method.  Perform all inherited behavior and mail any content
        just rolled out of the current log file.
        """

        super(LogSummarizingHandler, self).doRollover()
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

    def summary_due(self):
        """
        Determine if a summary is needed based on age.

        @return:    C{True} iff logged messages are sufficiently aged.
        @rtype:     bool
        """
        age = time() - self._log_state.last_rollover
        due = age > self.mirrmaid_config.summary_interval
        # Class state is for summary body, which is cumulative via boolean OR.
        # Method return value must remain distinct as to what is true right now
        # whereas the class state is what has been true since last
        # notification.
        self._rolled_for_age |= due
        return due

    def shouldRollover(self, record):
        """
        Determine if a rollover is needed.

        A rollover is needed whenever:
            1) the log attains a certain minimum size
            2) the log contains content that has attained a certain minimum age

        @param record:  Log record about to be committed.
        @type record:   LogRecord

        @return:    C{True} iff a rollover is needed for any reason.
        @rtype:     bool
        """
        for_size = super(LogSummarizingHandler, self).shouldRollover(record)
        for_age = self.summary_due()
        # Class state is for summary body, which is cumulative via boolean OR.
        # Method return value must remain distinct as to what is true right now
        # whereas the class state is what has been true since last
        # notification.
        self._rolled_for_size |= for_size
        return for_age or for_size
