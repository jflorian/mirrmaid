# coding=utf-8

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2016-2018 John Florian <jflorian@doubledog.org>
#
# This file is part of mirrmaid.

from logging import Filter, _checkLevel

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2016-2018 John Florian"""


class MaxLevelFilter(Filter):
    """Pass through all messages below a specified logging level."""

    def __init__(self, level):
        super().__init__()
        self.level = _checkLevel(level)

    def filter(self, record):
        # logger.setLevel is inclusive so this must be exclusive
        return record.levelno < self.level
