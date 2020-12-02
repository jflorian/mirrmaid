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
from signal import SIGHUP, SIGINT, SIGQUIT, SIGTERM, signal
from time import sleep

import yaml
from doubledog.config.sectioned import DefaultConfig

from mirrmaid.config import MirrmaidConfig, MirrorConfig, MirrorsConfig
from mirrmaid.constants import *
from mirrmaid.exceptions import MirrmaidRuntimeException, SignalException
from mirrmaid.logging.handlers import ConsoleHandler
from mirrmaid.logging.kludge import race_friendly_rotator
from mirrmaid.logging.summarizer import LogSummarizingHandler
from mirrmaid.synchronizer import Synchronizer

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2009-2020 John Florian"""

_log = logging.getLogger('mirrmaid')


class MirrorManager(object):
    def __init__(self, cli):
        """
        :param cli:
            The MirrmaidCLI instance using this MirrorManager.
        """
        self.cli = cli
        self.mirrmaid_conf = None
        self.default_conf = None
        self.mirrors_conf = None
        self._workers = None
        self._drop_privileges()
        self._init_logger()

    @property
    def _number_of_active_workers(self) -> int:
        worker: Synchronizer
        count = 0
        for worker in self._workers:
            if worker.is_alive():
                count += 1
        return count

    def _config_logger(self):
        for handler in logging.getLogger().handlers:
            if isinstance(handler, ConsoleHandler):
                handler.setLevel(self.cli.args.log_level)
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
                             RSYNC_PROXY, self.cli.args.config_filename)
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

    @staticmethod
    def _drop_privileges():
        """Drop privileges, if necessary, to run as correct user/group."""
        fail_msg = (f'could not drop privileges to USER/GROUP '
                    f'{RUNTIME_USER!r}/{RUNTIME_GROUP!r} '
                    f'because:')
        try:
            runtime_uid = pwd.getpwnam(RUNTIME_USER).pw_uid
        except KeyError:
            raise MirrmaidRuntimeException(
                f'{fail_msg} user {RUNTIME_USER!r} not found') from None
        try:
            runtime_gid = grp.getgrnam(RUNTIME_GROUP).gr_gid
        except KeyError:
            raise MirrmaidRuntimeException(
                f'{fail_msg} group {RUNTIME_USER!r} not found') from None
        if os.getuid() != runtime_uid or os.getgid() != runtime_gid:
            try:
                os.setgroups([])
                os.setgid(runtime_gid)
                os.setuid(runtime_uid)
            except OSError as e:
                raise MirrmaidRuntimeException(f'{fail_msg} {e}') from None
        os.umask(0o077)

    @staticmethod
    def _init_logger():
        with open(LOGGING_CONFIG_FILENAME) as f:
            logging.config.dictConfig(yaml.safe_load(f.read()))

    @staticmethod
    def _log_environment():
        for k in sorted(os.environ):
            _log.debug('environment: %s=%r', k, os.environ[k])

    def _signal_handler(self, signal_, _):
        """React to signals to bring about graceful shutdown of workers."""
        worker: Synchronizer
        _log.debug('caught signal %r; halting all workers', signal_)
        for worker in self._workers:
            worker.stop()
        _log.debug('all workers stopped or killed; shutting down')
        raise SignalException(f'caught signal {signal_!r}')

    def _wait_for_worker_limits(self):
        """Sleep until capacity is below resource limits."""
        while self._number_of_active_workers >= self.mirrmaid_conf.max_workers:
            _log.debug('%d of %d max workers are active',
                       self._number_of_active_workers,
                       self.mirrmaid_conf.max_workers)
            _log.debug('waiting for a worker to retire before starting more')
            sleep(60)

    def run(self):
        self._config_logger()
        _log.debug('using config file: %r', self.cli.args.config_filename)
        self.mirrmaid_conf = MirrmaidConfig(self.cli.args.config_filename)
        self._config_proxy()
        self._config_summarizer()
        self._log_environment()
        self.default_conf = DefaultConfig(self.cli.args.config_filename)
        self.mirrors_conf = MirrorsConfig(self.cli.args.config_filename)
        _log.debug('enabled mirrors: %r', self.mirrors_conf.mirrors)
        self._config_signal_handler()
        self._workers = []
        for mirror in self.mirrors_conf.mirrors:
            self._wait_for_worker_limits()
            _log.debug('processing mirror: %r', mirror)
            worker = Synchronizer(
                self.default_conf,
                MirrorConfig(self.cli.args.config_filename, mirror),
                dry_run=self.cli.args.dry_run,
            )
            self._workers.append(worker)
            worker.start()
