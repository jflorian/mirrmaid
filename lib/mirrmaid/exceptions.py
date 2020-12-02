# coding=utf-8

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2012-2020 John Florian <jflorian@doubledog.org>
#
# This file is part of mirrmaid.


"""
This module implements all Exception classes for the mirrmaid package.
"""

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2012-2020 John Florian"""


class MirrmaidRootException(Exception):
    pass


class MirrmaidRuntimeException(Exception):
    pass


class SignalException(MirrmaidRootException):
    pass


class SynchronizerException(MirrmaidRootException):
    pass
