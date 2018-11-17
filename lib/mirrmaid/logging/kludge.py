# coding=utf-8

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2016-2018 John Florian <jflorian@doubledog.org>
#
# This file is part of mirrmaid.


"""
This module implements kludges to work around bugs in the logging package of the
Python standard library.
"""

import logging.handlers
import os

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2016-2018 John Florian"""

_log = logging.getLogger()


def race_friendly_rotator(source: str, dest: str):
    """
    This function provides a multi-process friendly version of the
    BaseRotatingHandler.rotate() method (from the Python standard library)
    which does not suffer from race conditions.

    :param source:
        The source filename.  This is normally the base filename, e.g.
        'test.log'
    :param dest:
        The destination filename.  This is normally what the source is rotated
        to, e.g. 'test.log.1'.
    """
    try:
        os.rename(source, dest)
    except FileNotFoundError as e:
        _log.debug(
            'ignoring {} since it is likely due to a race condition'.format(e)
        )
