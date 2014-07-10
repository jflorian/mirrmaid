# coding=utf-8
# Copyright 2009-2014 John Florian <jflorian@doubledog.org>
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
This module implements the Configuration_Parser, which parses the
configuration file to make the directives readily available.
"""

from doubledog.config import BaseConfig

from mirrmaid.constants import *

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2009-2014 John Florian"""


class MirrmaidConfig(BaseConfig):
    """
    Accessor to the C{'MIRRMAID'} section within the mirrmaid configuration
    file.
    """

    def __init__(self, filename):
        """
        Initialize the MirrmaidConfig object for the configuration file..

        This file must contain a section named C{'MIRRMAID'}.

        @param filename:    Name of configuration file.
        @type filename:     str
        """
        BaseConfig.__init__(self, filename)
        self._set_section('MIRRMAID')

    @property
    def proxy(self):
        """
        @return:    The value of the optional C{'proxy'} setting.  If unset,
            the application default will be returned instead.
        @rtype:     str
        """
        return self.get('proxy', required=False, default=DEFAULT_PROXY)

    @property
    def summary_group(self):
        """
        @return:    The value of the optional C{'summary_group'} setting.  If
            unset, the application default will be returned instead.
        @rtype:     str
        """
        return self.get('summary_group', required=False,
                        default=DEFAULT_SUMMARY_GROUP)

    @property
    def summary_history_count(self):
        """
        @return:    The value of the optional C{'summary_history_count'}
            setting.  If unset, the application default will be returned
            instead.
        @rtype:     int
        """
        return max(
            1,
            self.get_int('summary_history_count', required=False,
                         default=DEFAULT_SUMMARY_HISTORY_COUNT)
        )

    @property
    def summary_interval(self):
        """
        @return:    The value of the optional C{'summary_interval'} setting.
            If unset, the application default will be returned instead.
        @rtype:     int
        """
        return max(
            600,
            self.get_int('summary_interval', required=False,
                         default=DEFAULT_SUMMARY_INTERVAL)
        )

    @property
    def summary_recipients(self):
        """
        @return:    The value of the optional C{'summary_recipients'} setting.
            If unset, the application default will be returned instead.
        @rtype:     list of str
        """
        return self.get_list('summary_recipients', required=False,
                             default=DEFAULT_SUMMARY_RECIPIENTS)

    @property
    def summary_size(self):
        """
        @return:    The value of the optional C{'summary_size'} setting.  If
            unset, the application default will be returned instead.
        @rtype:     int
        """
        return self.get_int('summary_size', required=False,
                            default=DEFAULT_SUMMARY_SIZE)


class MirrorsConfig(BaseConfig):
    """
    Accessor to the C{'MIRRORS'} section within the mirrmaid configuration
    file.
    """

    def __init__(self, filename):
        """
        Initialize the MirrorsConfig object for the configuration file.

        This file must contain a section named C{'MIRRORS'}.

        @param filename:    Name of configuration file.
        @type filename:     str
        """

        BaseConfig.__init__(self, filename)
        self._set_section('MIRRORS')

    @property
    def mirrors(self):
        """
        Return a list of those mirror names that are enabled.

        @return:    The value of the required C{'enabled'} setting.
        @rtype:     list of str

        @raise NoOptionError:   If the setting is absent.
        @raise NoSectionError:  If the section is absent.
        """

        return self.get_list('enabled')


class MirrorConfig(BaseConfig):
    """
    Accessor to a specific mirror's section within the mirrmaid configuration
    file.
    """
    """Accessor to a named mirror's configuration section."""

    def __init__(self, filename, mirror):
        """
        Initialize the MirrorConfig object for the configuration file.

        This file must contain a section named I{mirror}.

        @param filename:    Name of configuration file.
        @type filename:     str

        @param mirror:  Name of configuration section for a specific mirror.
        @type filename: str
        """

        BaseConfig.__init__(self, filename)
        self._set_section(mirror)

    @property
    def excludes(self):
        """
        Return a list of the exclusion patterns for the mirror synchronization.

        @return:    The value of the required C{'exclude'} setting.
        @rtype:     list of str

        @raise NoOptionError:   If the setting is absent.
        @raise NoSectionError:  If the section is absent.
        """

        return self.get_list('exclude')

    @property
    def includes(self):
        """
        Return a list of the inclusion patterns for the mirror synchronization.

        @return:    The value of the required C{'include'} setting.
        @rtype:     list of str

        @raise NoOptionError:   If the setting is absent.
        @raise NoSectionError:  If the section is absent.
        """

        return self.get_list('include')

    @property
    def mirror_name(self):
        """
        @return:    The name of the mirror.
        @rtype:     str

        @raise NoOptionError:   If the setting is absent.
        @raise NoSectionError:  If the section is absent.
        """

        return self._get_section()

    @property
    def source(self):
        """
        Return the source for the mirror synchronization.

        @return:    The value of the required C{'source'} setting.
        @rtype:     str

        @raise NoOptionError:   If the setting is absent.
        @raise NoSectionError:  If the section is absent.
        """

        return self.get('source')

    @property
    def target(self):
        """
        Return the target for the mirror synchronization.

        @return:    The value of the required C{'target'} setting.
        @rtype:     str

        @raise NoOptionError:   If the setting is absent.
        @raise NoSectionError:  If the section is absent.
        """

        return self.get('target')
