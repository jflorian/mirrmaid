#!/usr/bin/python3 -Es
# coding=utf-8


# Copyright 2009-2015 John Florian <jflorian@doubledog.org>
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


__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2009-2015 John Florian"""


import os
import sys

from mirrmaid.manager import MirrorManager


MirrorManager(sys.argv[1:]).run()
sys.exit(os.EX_OK)
