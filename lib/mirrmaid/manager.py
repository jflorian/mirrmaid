# coding=utf-8

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2009-2018 John Florian <jflorian@doubledog.org>
#
# This file is part of mirrmaid.


"""
This module implements the MirrorManager, which directs the mirroring
activities of one or more Mirror_Synchronizers.
"""

import grp
import logging
import logging.config
import logging.handlers
import os
import pwd
import sys
from argparse import ArgumentParser
from traceback import format_exc

import yaml
from doubledog.config.sectioned import DefaultConfig, InvalidConfiguration

from mirrmaid.config import MirrorConfig, MirrorsConfig, MirrmaidConfig
from mirrmaid.constants import *
from mirrmaid.exceptions import SynchronizerException
from mirrmaid.logging.handlers import ConsoleHandler
from mirrmaid.logging.kludge import race_friendly_rotator
from mirrmaid.logging.summarizer import LogSummarizingHandler
from mirrmaid.synchronizer import Synchronizer

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2009-2018 John Florian"""

_log = logging.getLogger('mirrmaid')


class MirrorManager(object):
    def __init__(self, args):
        self.args = args
        self._drop_privileges()
        self.parser = None
        self._init_logger()

    def _config_logger(self):
        for handler in logging.getLogger().handlers:
            if isinstance(handler, ConsoleHandler):
                handler.setLevel(self.args.log_level)
            if isinstance(handler, logging.handlers.BaseRotatingHandler):
                handler.rotator = race_friendly_rotator

    def _config_proxy(self):
        """Configure the rsync proxy."""
        proxy = self.mirrmaid_conf.proxy
        if proxy is None:
            try:
                del os.environ[RSYNC_PROXY]
            except KeyError:
                pass
            else:
                _log.warning(
                    'environment variable {!r} has been unset; use the "proxy" '
                    'setting in {} instead if proxy support is required'.format(
                        RSYNC_PROXY,
                        self.args.config_filename,
                    )
                )
            _log.debug('will not proxy rsync')
        else:
            os.environ[RSYNC_PROXY] = proxy
            _log.debug('will proxy rsync through {!r}'.format(proxy))

    def _config_summarizer(self):
        handler = LogSummarizingHandler(self.mirrmaid_conf)
        handler.setFormatter(LOGGING_FORMATTER)
        handler.setLevel(logging.ERROR)
        _log.addHandler(handler)
        # Ensure the summary is delivered regularly, even if no messages are
        # logged there during this run.
        if handler.summary_due:
            handler.force_rollover()

    def _drop_privileges(self):
        """Drop privileges, if necessary, to run as correct user/group."""
        runtime_uid = pwd.getpwnam(RUNTIME_USER).pw_uid
        runtime_gid = grp.getgrnam(RUNTIME_GROUP).gr_gid
        if os.getuid() != runtime_uid or os.getgid() != runtime_gid:
            try:
                os.setgroups([])
                os.setgid(runtime_gid)
                os.setuid(runtime_uid)
            except OSError as e:
                self._exit(
                    os.EX_OSERR,
                    'could not drop privileges to USER/GROUP {!r}/{!r} '
                    'because: {}'.format(
                        RUNTIME_USER,
                        RUNTIME_GROUP,
                        e,
                    )
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

    @staticmethod
    def _init_logger():
        with open(LOGGING_CONFIG_FILENAME) as f:
            logging.config.dictConfig(yaml.safe_load(f.read()))

    @staticmethod
    def _log_environment():
        for k in sorted(os.environ):
            _log.debug(
                'environment: {}={!r}'.format(k, os.environ[k])
            )

    def _parse_args(self):
        self.parser = ArgumentParser()
        self.parser.set_defaults(
            config_filename=CONFIG_FILENAME,
            log_level=logging.WARNING
        )
        self.parser.add_argument(
            '-c', '--config',
            dest='config_filename',
            help='use alternate configuration file'
        )
        self.parser.add_argument(
            '-d', '--debug',
            action='store_const', dest='log_level', const=logging.DEBUG,
            help='set logging level to DEBUG',
        )
        self.parser.add_argument(
            '-v', '--verbose',
            action='store_const', dest='log_level', const=logging.INFO,
            help='set logging level to INFO',
        )
        self.args = self.parser.parse_args()

    def _run(self):
        self._parse_args()
        self._config_logger()
        _log.debug(
            'using config file: {!r}'.format(self.args.config_filename)
        )
        self.mirrmaid_conf = MirrmaidConfig(self.args.config_filename)
        self._config_proxy()
        self._config_summarizer()
        self._log_environment()
        self.default_conf = DefaultConfig(self.args.config_filename)
        self.mirrors_conf = MirrorsConfig(self.args.config_filename)
        _log.debug(
            'enabled mirrors: {!r}'.format(self.mirrors_conf.mirrors)
        )
        for mirror in self.mirrors_conf.mirrors:
            _log.debug('processing mirror: {!r}'.format(mirror))
            worker = Synchronizer(
                self.default_conf,
                MirrorConfig(self.args.config_filename, mirror)
            )
            worker.run()

    def run(self):
        # noinspection PyBroadException
        try:
            self._run()
        except InvalidConfiguration as e:
            _log.critical('invalid configuration:\n{0}'.format(e))
            self._exit(os.EX_CONFIG)
        except SynchronizerException as e:
            _log.critical(e)
            self._exit(os.EX_OSERR, e)
        except KeyboardInterrupt:
            _log.error('interrupted via SIGINT')
            self._exit(os.EX_OSERR)
        except SystemExit:
            pass  # presumably already handled
        except:
            _log.critical('unhandled exception:\n{0}'.format(format_exc()))
            self._exit(os.EX_SOFTWARE)
        finally:
            logging.shutdown()
