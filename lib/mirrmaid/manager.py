# coding=utf-8
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
This module implements the MirrorManager, which directs the mirroring
activities of one or more Mirror_Synchronizers.
"""

import grp
import logging
import logging.handlers
from optparse import OptionParser
import os
import pwd
import sys
from traceback import format_exc

from doubledog.config import DefaultConfig, InvalidConfiguration

from mirrmaid.config import MirrorConfig, MirrorsConfig, MirrmaidConfig
from mirrmaid.constants import *
from mirrmaid.summarizer import LogSummarizingHandler
from mirrmaid.synchronizer import Synchronizer, SynchronizerException


__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2009-2014 John Florian"""


class MirrorManager(object):
    def __init__(self, args):
        self.args = args
        self._drop_privileges()
        self.options = None
        self.parser = None
        self._init_logger()

    def _config_logger(self):
        self.log.setLevel(self.options.log_level * 10)
        if self.options.debug:
            console = logging.StreamHandler()
            console.setFormatter(CONSOLE_FORMATTER)
            self.log.addHandler(console)

    def _config_proxy(self):
        """Configure the rsync proxy."""
        proxy = self.mirrmaid_conf.proxy
        if proxy is None:
            try:
                del os.environ[RSYNC_PROXY]
            except KeyError:
                pass
            else:
                self.log.warning(
                    'environment variable "{0}" has been unset; '
                    'use the "proxy" setting in {1} instead '
                    'if proxy support is required'.format(
                        RSYNC_PROXY, self.options.config_filename))
            self.log.debug('will not proxy rsync')
        else:
            os.environ[RSYNC_PROXY] = proxy
            self.log.debug('will proxy rsync through "{0}"'.format(proxy))

    def _config_summarizer(self):
        handler = LogSummarizingHandler(self.mirrmaid_conf)
        handler.setFormatter(LOGGING_FORMATTER)
        handler.setLevel(logging.ERROR)
        self.log.addHandler(handler)
        # Ensure the summary is delivered regularly, even if no messages are
        # logged there during this run.
        if handler.summary_due():
            handler.force_rollover()

    def _drop_privileges(self):
        """Drop privileges, if necessary, to run as correct user/group."""
        runtime_uid = pwd.getpwnam(RUNTIME_USER).pw_uid
        runtime_gid = grp.getgrnam(RUNTIME_GROUP).gr_gid
        if os.getuid() != runtime_uid and os.getgid() != runtime_gid:
            try:
                os.setgroups([])
                os.setgid(runtime_gid)
                os.setuid(runtime_uid)
            except OSError as e:
                self._exit(
                    os.EX_OSERR,
                    'could not drop privileges to USER/GROUP "{0}/{1}" '
                    'because: {2}'
                    .format(RUNTIME_USER, RUNTIME_GROUP, e)
                )
        os.umask(0o077)

    def _exit(self, exit_code=os.EX_OK, message=None, show_help=False):
        """
        Cause the current command to exit.

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
                sys.stderr.write('\n** Error: {0}\n'.format(message))
            else:
                sys.stderr.write(message)
        sys.exit(exit_code)

    def _init_logger(self):
        self.log = logging.getLogger('mirrmaid')
        handler = logging.handlers.TimedRotatingFileHandler(
            LOG_FILENAME, when='midnight', backupCount=7)
        handler.setFormatter(LOGGING_FORMATTER)
        self.log.addHandler(handler)

    def _log_environment(self):
        for k in sorted(os.environ):
            self.log.debug('environment: {0}={1}'.format(k, os.environ[k]))

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

    def _run(self):
        self._parse_options()
        self._config_logger()
        self.log.debug(
            'using config file: {0}'.format(self.options.config_filename))
        self.mirrmaid_conf = MirrmaidConfig(self.options.config_filename)
        self._config_proxy()
        self._config_summarizer()
        self._log_environment()
        self.default_conf = DefaultConfig(self.options.config_filename)
        self.mirrors_conf = MirrorsConfig(self.options.config_filename)
        self.log.debug(
            'enabled mirrors: {0}'.format(self.mirrors_conf.mirrors))
        for mirror in self.mirrors_conf.mirrors:
            self.log.debug('processing mirror: "{0}"'.format(mirror))
            worker = Synchronizer(
                self.default_conf,
                MirrorConfig(self.options.config_filename, mirror)
            )
            worker.run()

    def run(self):
        # noinspection PyBroadException
        try:
            self._run()
        except InvalidConfiguration as e:
            self.log.critical('invalid configuration:\n{0}'.format(e))
            self._exit(os.EX_CONFIG)
        except SynchronizerException as e:
            self.log.critical(e)
            self._exit(os.EX_OSERR, e)
        except KeyboardInterrupt:
            self.log.error('interrupted via SIGINT')
            self._exit(os.EX_OSERR)
        except SystemExit:
            pass  # presumably already handled
        except:
            self.log.critical('unhandled exception:\n{0}'.format(format_exc()))
            self._exit(os.EX_SOFTWARE)
        finally:
            logging.shutdown()
