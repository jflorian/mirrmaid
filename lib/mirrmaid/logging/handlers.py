# coding=utf-8

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2016-2018 John Florian <jflorian@doubledog.org>
#
# This file is part of mirrmaid.

from logging import StreamHandler

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2016-2018 John Florian"""


class ConsoleHandler(StreamHandler):
    """
    This is identical to the standard StreamHandler, but provides a reliable
    means for identifying the one dedicated for console use distinctly from any
    other StreamHandler instances that may be present.
    """
    pass
