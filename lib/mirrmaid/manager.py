# coding=utf-8

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2009-2020 John Florian <jflorian@doubledog.org>
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
from signal import SIGHUP, SIGINT, SIGQUIT, SIGTERM, signal
from traceback import format_exc

import yaml
from doubledog.config.sectioned import DefaultConfig, InvalidConfiguration

from mirrmaid.config import MirrmaidConfig, MirrorConfig, MirrorsConfig
from mirrmaid.constants import *
from mirrmaid.exceptions import SignalException, SynchronizerException
from mirrmaid.logging.handlers import ConsoleHandler
from mirrmaid.logging.kludge import race_friendly_rotator
from mirrmaid.logging.summarizer import LogSummarizingHandler
from mirrmaid.synchronizer import Synchronizer

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2009-2020 John Florian"""

_log = logging.getLogger('mirrmaid')


class MirrorManager(object):
    def __init__(self, args):
        self.args = args
        self._drop_privileges()
        self.parser = None
        self._workers = None
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
                _log.warning('environment variable %r has been unset; '
                             'use the "proxy" setting in %r instead if proxy '
                             'support is required',
                             RSYNC_PROXY, self.args.config_filename)
            _log.debug('will not proxy rsync')
        else:
            os.environ[RSYNC_PROXY] = proxy
            _log.debug('will proxy rsync through %r', proxy)

    def _config_signal_handler(self):
        """Register a signal handler for graceful shutdowns."""
        for signal_ in [SIGHUP, SIGINT, SIGQUIT, SIGTERM]:
            _log.debug('setting trap for signal %r', signal_)
            signal(signal_, self._signal_handler)

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
                self._exit(os.EX_OSERR,
                           f'could not drop privileges to USER/GROUP'
                           f' {RUNTIME_USER!r}/{RUNTIME_GROUP!r} because: {e}')
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
                sys.stderr.write(f'\n** Error: {message}\n')
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
            _log.debug('environment: %s=%r', k, os.environ[k])

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
        _log.debug('using config file: %r', self.args.config_filename)
        self.mirrmaid_conf = MirrmaidConfig(self.args.config_filename)
        self._config_proxy()
        self._config_summarizer()
        self._log_environment()
        self.default_conf = DefaultConfig(self.args.config_filename)
        self.mirrors_conf = MirrorsConfig(self.args.config_filename)
        _log.debug('enabled mirrors: %r', self.mirrors_conf.mirrors)
        self._config_signal_handler()
        self._workers = []
        for mirror in self.mirrors_conf.mirrors:
            _log.debug('processing mirror: %r', mirror)
            worker = Synchronizer(
                self.default_conf,
                MirrorConfig(self.args.config_filename, mirror)
            )
            self._workers.append(worker)
            worker.start()

    def _signal_handler(self, signal_, _):
        """React to signals to bring about graceful shutdown of workers."""
        worker: Synchronizer
        _log.debug('caught signal %r; halting all workers', signal_)
        for worker in self._workers:
            worker.stop()
        _log.debug('all workers stopped or killed; shutting down')
        raise SignalException(f'caught signal {signal_!r}')

    def run(self):
        # noinspection PyBroadException
        try:
            self._run()
        except InvalidConfiguration as e:
            _log.critical('invalid configuration:\n%s', e)
            self._exit(os.EX_CONFIG)
        except SynchronizerException as e:
            _log.critical(e)
            self._exit(os.EX_OSERR, e)
        except (KeyboardInterrupt, SignalException) as e:
            _log.error('interrupted via %s', e)
            self._exit(os.EX_OSERR)
        except SystemExit:
            pass  # presumably already handled
        except:
            _log.critical('unhandled exception:\n%s', format_exc())
            self._exit(os.EX_SOFTWARE)
        finally:
            logging.shutdown()
