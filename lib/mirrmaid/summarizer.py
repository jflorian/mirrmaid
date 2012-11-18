# Copyright 2012 John Florian <jflorian@doubledog.org>
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
import logging
import logging.handlers
import shelve
from time import time, ctime, asctime

from doubledog.mail import MiniMailer

# LOG_STATE controls where mirrmaid will persist internal data regarding the
# state of its logging and summary features.
LOG_STATE = '/var/lib/mirrmaid/log_state'

# SUMMARY_INTERVAL controls the maximum number of seconds that may elapse
# before a summary is automatically dispatched.  This can be useful in ensuring
# the operator receives periodic summaries, even when nothing special occurred.
# See also SUMMARY_MAX_BYTES in manager.py.
SUMMARY_INTERVAL = 24 * 60 * 60         #TODO
SUMMARY_INTERVAL = 24 * 60

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2012 John Florian"""


class LogState(object):
    """A trivial persistent shelf object for recording log rotation state."""

    LAST_ROLLOVER = 'last_rollover'

    def __init__(self):
        # Establish initial conditions such that it appears a log rollover has
        # just occurred, since that best matches the actual case of having an
        # emtpy log.  This ensures a rollover will occur in
        if self.last_rollover is None:
            self.last_rollover = time()

    @property
    def last_rollover(self):
        """Return the number of seconds since the last rollover."""

        shelf = None
        try:
            shelf = shelve.open(LOG_STATE)
            return shelf[self.LAST_ROLLOVER]
        except KeyError:
            return None
        finally:
            if shelf:
                shelf.close()

    @last_rollover.setter
    def last_rollover(self, when):
        """Record the time of rollover."""

        shelf = None
        try:
            shelf = shelve.open(LOG_STATE)
            shelf[self.LAST_ROLLOVER] = when
        finally:
            if shelf:
                shelf.close()


class LogSummarizingHandler(logging.handlers.RotatingFileHandler):
    """This class extends the RotatingFileHandler with an additional rollover
    trigger based on the elapsed time since the last rollover.  Thus this
    handler ensure the log gets a rollover whenever maxBytes is exceeded or
    when the elapsed time exceeds SUMMARY_INTERVAL, whichever occurs first.

    When a rollover does occur, the log content just displaced will be
    delivered via email as a means of summarizing the important messages that
    had occurred during this most recent SUMMARY_INTERVAL.
    """

    def __init__(self, *args, **kwargs):
        self._log_state = LogState()
        super(LogSummarizingHandler, self).__init__(*args, **kwargs)

    def _mail_summary(self):
        # TODO: make recipients configurable
        MiniMailer().send('mirrmaid', 'root', 'mirrmaid Activity Summary',
                          self._summary_body())

    def _summary_body(self):
        since = ctime(self._log_state.last_rollover)
        until = asctime()
        with open('{}.1'.format(self.baseFilename), 'r') as f:
            log_content = f.read()
        body = [
            'Since:\t{}'.format(since),
            'Until:\t{}'.format(until),
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
        """Overridden method.  Perform all inherited behavior and mail any
        content just rolled out of the current log file.
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
        age = time() - self._log_state.last_rollover
        return age > SUMMARY_INTERVAL

    def shouldRollover(self, record):
        result = super(LogSummarizingHandler, self).shouldRollover(record)
        result |= self.summary_due()
        return result

