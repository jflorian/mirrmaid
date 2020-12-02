# coding=utf-8

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2020 John Florian <jflorian@doubledog.org>
#
# This file is part of mirrmaid.

import logging
import os
import sys
from argparse import ArgumentParser
from traceback import format_exc

from doubledog.config.sectioned import InvalidConfiguration

from mirrmaid.constants import CONFIG_FILENAME
from mirrmaid.exceptions import (
    MirrmaidRuntimeException, SignalException,
    SynchronizerException,
)
from mirrmaid.manager import MirrorManager

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2020 John Florian"""

_log = logging.getLogger('mirrmaid')


class MirrmaidCLI(object):
    def __init__(self):
        self.args = None
        self._init_parser()
        self.run()

    def _init_parser(self):
        self._parser = ArgumentParser()
        self._parser.set_defaults(
            config_filename=CONFIG_FILENAME,
            log_level=logging.WARNING
        )
        self._parser.add_argument(
            '-c', '--config',
            dest='config_filename',
            help='use alternate configuration file'
        )
        self._parser.add_argument(
            '-d', '--debug',
            action='store_const', dest='log_level', const=logging.DEBUG,
            help='set logging level to DEBUG',
        )
        self._parser.add_argument(
            '-n', '--dry-run',
            action='store_true',
            help='perform a trial run with no changes made',
        )
        self._parser.add_argument(
            '-v', '--verbose',
            action='store_const', dest='log_level', const=logging.INFO,
            help='set logging level to INFO',
        )

    def exit(self, exit_code=os.EX_OK, message=None, show_help=False):
        """
        Terminate the CLI execution.

        If provided, the message will be shown; presumably containing the
        reason.  An exit code will be provided for the caller and if this
        value is non-zero, the message will be prefixed to indicate that it is
        an error.  The caller of this method may also request that the help
        also be shown.
        """
        if show_help:
            self._parser.print_help()
        if message:
            if exit_code:
                sys.stderr.write(f'\n** Error: {message}\n')
            else:
                sys.stderr.write(message)
        sys.exit(exit_code)

    def run(self):
        # noinspection PyBroadException
        try:
            self.args = self._parser.parse_args()
            MirrorManager(self).run()
        except InvalidConfiguration as e:
            _log.critical('invalid configuration:\n%s', e)
            self.exit(os.EX_CONFIG)
        except (MirrmaidRuntimeException, SynchronizerException) as e:
            _log.critical(e)
            self.exit(os.EX_OSERR, e)
        except (KeyboardInterrupt, SignalException) as e:
            _log.error('interrupted via %s', e)
            self.exit(os.EX_OSERR)
        except SystemExit:
            pass  # presumably already handled
        except Exception:
            _log.critical('unhandled exception:\n%s', format_exc())
            self.exit(os.EX_SOFTWARE)
        finally:
            logging.shutdown()
