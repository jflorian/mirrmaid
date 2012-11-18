# Copyright 2009-2012 John Florian <jflorian@doubledog.org>
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
This module implements the Mirror_Manager, which directs the mirroring
activities of one or more Mirror_Synchronizers.
"""

from optparse import OptionParser
from traceback import format_exc
import logging
import logging.handlers
import os
import sys

from doubledog.config import DefaultConfig, InvalidConfiguration
from mirrmaid.config import Mirror_Config, Mirrors_Config
from mirrmaid.summarizer import LogSummarizingHandler
from mirrmaid.synchronizer import Synchronizer, Synchronizer_Exception

# CONFIG_FILENAME controls the default run-time configuration file.
CONFIG_FILENAME = '/etc/mirrmaid/mirrmaid.conf'

# LOG_FILENAME controls the primary, detailed log file.
LOG_FILENAME = '/var/log/mirrmaid/mirrmaid'

# SUMMARY_FILENAME controls the less-detailed log file, which typically
# captures only messages at level ERROR or higher.
SUMMARY_FILENAME = '/var/log/mirrmaid/summary'

# SUMMARY_HISTORY_COUNT controls the number of historical copies of
# SUMMARY_FILENAME.  While at least one copy must be retained, you may elect
# to keep more.
SUMMARY_HISTORY_COUNT = 3

# SUMMARY_MAX_BYTES controls the maximum file size (in bytes) that
# SUMMARY_FILENAME may reach before a summary is automatically dispatched.
# This can be useful in alerting the operator that something is awry before
# the normal SUMMARY_INTERVAL (see summarizer.py) has expired.
SUMMARY_MAX_BYTES = 20000

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2009-2012 John Florian"""


class Mirror_Manager(object):
    def __init__(self, args):
        self.args = args
        self.options = None
        self.parser = None
        self._init_logger()

    def _config_logger(self):
        self.log.setLevel(self.options.log_level * 10)
        if self.options.debug:
            console = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(name)s %(levelname)-8s %(message)s')
            console.setFormatter(formatter)
            self.log.addHandler(console)

    def _exit(self, exit_code=os.EX_OK, message=None, show_help=False):
        """Cause the current command to exit.

        If provided, the message will be shown; presumably containing the
        reason.  An exit code will be provided for the caller and if this
        value is non-zero, the message will be prefixed to indicate that it is
        an error.  The caller of this method may also request that the help
        also be shown.
        """
        if show_help:
            self.parser.print_help()
        if message:
            if exit_code:
                sys.stderr.write('\n** Error: %s\n' % message)
            else:
                sys.stderr.write(message)
        sys.exit(exit_code)

    def _init_logger(self):
        self.log = logging.getLogger('manager')
        formatter = logging.Formatter(
            '%(asctime)s %(name)s[%(process)d] %(levelname)-8s %(message)s')
        handler = logging.handlers.TimedRotatingFileHandler(
            LOG_FILENAME, when='midnight', backupCount=7)
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        handler = LogSummarizingHandler(
            SUMMARY_FILENAME,
            maxBytes=SUMMARY_MAX_BYTES,
            backupCount=max(1, SUMMARY_HISTORY_COUNT))
        handler.setFormatter(formatter)
        handler.setLevel(logging.ERROR)
        self.log.addHandler(handler)
        # Ensure the summary is delivered regularly, even if no messages are
        # logged there during this run.
        if handler.summary_due():
            handler.force_rollover()

    def _parse_options(self):
        self.parser = OptionParser(usage='Usage: mirrmaid [options]')
        self.parser.add_option('-c', '--config',
                               type='string', dest='config_filename',
                               help='use alternate configuration file')
        self.parser.add_option('-d', '--debug',
                               action='store_true', dest='debug',
                               help='enable logging to console')
        self.parser.add_option('-l', '--level',
                               type='int', dest='log_level',
                               help=('set minimum logging threshold '
                                     '(1=debug, 2=info[default], 3=warning, '
                                     '4=error, 5=critical'))
        self.parser.set_defaults(config_filename=CONFIG_FILENAME, debug=False,
                                 log_level=2)
        self.options, self.args = self.parser.parse_args()
        if len(self.args):
            self._exit(os.EX_USAGE, 'No arguments expected.', show_help=True)
        if self.options.log_level not in range(1, 6):
            self._exit(os.EX_USAGE,
                       'LOG_LEVEL must not be less than 1 nor greater than 5.')

    def run(self):
        #noinspection PyBroadException
        try:
            self._parse_options()
            self._config_logger()
            self.log.debug('using config file: %s' %
                           self.options.config_filename)
            for k in sorted(os.environ):
                self.log.debug('environment: %s=%s' % (k, os.environ[k]))
            self.default_conf = DefaultConfig(self.options.config_filename)
            self.mirrors_conf = Mirrors_Config(self.options.config_filename)
            mirrors = self.mirrors_conf.get_mirrors()
            self.log.debug('enabled mirrors: %s' % mirrors)
            for mirror in mirrors:
                self.log.debug('processing mirror: "%s"' % mirror)
                worker = Synchronizer(
                    self.default_conf,
                    Mirror_Config(self.options.config_filename, mirror)
                )
                worker.run()
        except InvalidConfiguration as e:
            self.log.critical('invalid configuration:\n%s' % e)
            self._exit(os.EX_CONFIG)
        except Synchronizer_Exception as e:
            self.log.critical(e)
            self._exit(os.EX_OSERR, e)
        except KeyboardInterrupt:
            self.log.error('interrupted via SIGINT')
            self._exit(os.EX_OSERR)
        except SystemExit:
            pass        # presumably already handled
        except:
            self.log.critical('unhandled exception:\n%s' % format_exc())
            self._exit(os.EX_SOFTWARE)
        finally:
            logging.shutdown()
