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

from logging import Filter, _checkLevel

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2016 John Florian"""


class MaxLevelFilter(Filter):
    """Pass through all messages below a specified logging level."""

    def __init__(self, level):
        super().__init__()
        self.level = _checkLevel(level)

    def filter(self, record):
        # logger.setLevel is inclusive so this must be exclusive
        return record.levelno < self.level