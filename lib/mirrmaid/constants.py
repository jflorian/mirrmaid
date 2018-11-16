# coding=utf-8

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2012-2018 John Florian <jflorian@doubledog.org>
#
# This file is part of mirrmaid.


"""
This defines various constants for the mirrmaid package.
"""
from logging import Formatter

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2012-2018 John Florian"""

# The default run-time configuration file.
CONFIG_FILENAME = '/etc/mirrmaid/mirrmaid.conf'

# Format to be used when logging to console (i.e., when using the '-d' option).
CONSOLE_FORMATTER = Formatter('%(name)s %(levelname)-8s %(message)s')

# Default rsync proxy to use in 'HOST:PORT' format or None if no proxy is
# required.
DEFAULT_PROXY = None

# Default operations summary grouping tag.
DEFAULT_SUMMARY_GROUP = 'My Mirrors'

# Default number of historical operations summaries to keep around.
DEFAULT_SUMMARY_HISTORY_COUNT = 3

# Default interval, in seconds, between operations summaries.
DEFAULT_SUMMARY_INTERVAL = 24 * 60 * 60

# Default list of recipients to receive operations summary emails.  (List
# necessarily cast as a string here to emulate retrieval from configuration
# file.)
DEFAULT_SUMMARY_RECIPIENTS = '["root"]'

# Default threshold to force premature sending of operations summary.
DEFAULT_SUMMARY_SIZE = 20000

# The default run-time configuration file.
LOGGING_CONFIG_FILENAME = '/etc/mirrmaid/logging.yaml'

# Format to be used when logging to the main log file and the operations
# summary log file.
LOGGING_FORMATTER = Formatter(
    '%(asctime)s %(name)s[%(process)d] %(levelname)-8s %(message)s'
)

# Where run-time advisory lock files are created.
LOCK_DIRECTORY = '/run/lock/mirrmaid/'

# Where mirrmaid will persist internal data regarding the state of its
# logging and operations summary features.
LOG_STATE = '/var/lib/mirrmaid/log_state'

# Where the rsync executable can be found.
RSYNC = '/usr/bin/rsync'

# Name of environment variable used to configure rsync for proxy usage.
RSYNC_PROXY = 'RSYNC_PROXY'

# mirrmaid will drop (root) privileges, if necessary, to the following at
# startup.
RUNTIME_GROUP = 'mirrmaid'
RUNTIME_USER = 'mirrmaid'

# The operations summary log file, which captures only messages at level
# ERROR or higher.
SUMMARY_FILENAME = '/var/log/mirrmaid/summary'
