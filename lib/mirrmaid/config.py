# Copyright 2009, 2010 John Florian <jflorian@doubledog.org>
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


from doubledog.config import Config, Default_Config


"""
This module implements the Configuration_Parser, which parses the configuration file to make the directives
readily available.
"""


class Mirrors_Config(Config):
    """Accessor to the MIRRORS configuration section."""

    def __init__(self, filename):
        """Construct a Mirrors_Config object for the named configuration file."""

        Config.__init__(self, filename)
        self._set_section('MIRRORS')

    def get_mirrors(self):
        """Return a list of those mirror names that are enabled."""

        return eval(self.get('enabled'))


class Mirror_Config(Config):
    """Accessor to a named mirror's configuration section."""

    def __init__(self, filename, mirror):
        """Construct a Mirror_Config object for the named mirror section within the named configuration file."""

        Config.__init__(self, filename)
        self._set_section(mirror)

    def get_excludes(self):
        """Return a list of the exclusion patterns for the mirror synchronization."""

        return eval(self.get('exclude'))

    def get_includes(self):
        """Return a list of the inclusion patterns for the mirror synchronization."""

        return eval(self.get('include'))

    def get_mirror_name(self):
        """Return the name of the mirror for which this configuration applies."""

        return self._get_section()

    def get_source(self):
        """Return the source for the mirror synchronization."""

        return self.get('source')

    def get_target(self):
        """Return the target for the mirror synchronization."""

        return self.get('target')
