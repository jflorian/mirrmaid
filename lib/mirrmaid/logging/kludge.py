# coding=utf-8
# Copyright 2016 John Florian <jflorian@doubledog.org>
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
This module implements kludges to work around bugs in the logging package of the
Python standard library.
"""

import logging.handlers
import os

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2016 John Florian"""

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
