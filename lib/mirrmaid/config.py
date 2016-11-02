# coding=utf-8
# Copyright 2009-2016 John Florian <jflorian@doubledog.org>
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

from doubledog.config.sectioned import BaseConfig

from mirrmaid.constants import *

__author__ = """John Florian <jflorian@doubledog.org>"""
__copyright__ = """Copyright 2009-2016 John Florian"""


class MirrmaidConfig(BaseConfig):
    """
    Accessor to the ``'MIRRMAID'`` section within the mirrmaid configuration
    file.
    """

    def __init__(self, filename: str):
        """
        Initialize the MirrmaidConfig object for the configuration file..

        This file must contain a section named ``'MIRRMAID'``.

        :param filename:
            Name of configuration file.
        """
        BaseConfig.__init__(self, filename)
        self._set_section('MIRRMAID')

    @property
    def proxy(self) -> str:
        """
        :return:
            The value of the optional ``'proxy'`` setting.  If unset, the
            application default will be returned instead.
        """
        return self.get('proxy', required=False, default=DEFAULT_PROXY)

    @property
    def summary_group(self) -> str:
        """
        :return:
            The value of the optional ``'summary_group'`` setting.  If unset,
            the application default will be returned instead.
        """
        return self.get('summary_group', required=False,
                        default=DEFAULT_SUMMARY_GROUP)

    @property
    def summary_history_count(self) -> int:
        """
        :return:
            The value of the optional ``'summary_history_count'`` setting.  If
            unset, the application default will be returned instead.
        """
        return max(
            1,
            self.get_int('summary_history_count', required=False,
                         default=DEFAULT_SUMMARY_HISTORY_COUNT)
        )

    @property
    def summary_interval(self) -> int:
        """
        :return:
            The value of the optional ``'summary_interval'`` setting. If unset,
            the application default will be returned instead.
        """
        return max(
            600,
            self.get_int('summary_interval', required=False,
                         default=DEFAULT_SUMMARY_INTERVAL)
        )

    @property
    def summary_recipients(self) -> list:
        """
        :return:
            The value of the optional ``'summary_recipients'`` setting. If
            unset, the application default will be returned instead.
        """
        return self.get_list('summary_recipients', required=False,
                             default=DEFAULT_SUMMARY_RECIPIENTS)

    @property
    def summary_size(self) -> int:
        """
        :return:
            The value of the optional ``'summary_size'`` setting.  If unset, the
            application default will be returned instead.
        """
        return self.get_int('summary_size', required=False,
                            default=DEFAULT_SUMMARY_SIZE)


class MirrorsConfig(BaseConfig):
    """
    Accessor to the ``'MIRRORS'`` section within the mirrmaid configuration
    file.
    """

    def __init__(self, filename: str):
        """
        Initialize the MirrorsConfig object for the configuration file.

        This file must contain a section named ``'MIRRORS'``.

        :param filename:
            Name of configuration file.
        """
        BaseConfig.__init__(self, filename)
        self._set_section('MIRRORS')

    @property
    def mirrors(self) -> list:
        """
        :return:
            Return a list of those mirror names that are enabled -- the value of
            the required ``'enabled'`` setting.

        :raises NoOptionError:
            If the setting is absent.
        :raises NoSectionError:
            If the section is absent.
        """
        return self.get_list('enabled')


class MirrorConfig(BaseConfig):
    """
    Accessor to a specific mirror's section within the mirrmaid configuration
    file.
    """
    """Accessor to a named mirror's configuration section."""

    def __init__(self, filename: str, mirror: str):
        """
        Initialize the MirrorConfig object for the configuration file.

        This file must contain a section named *mirror*.

        :param filename:
            Name of configuration file.

        :param mirror:
            Name of configuration section for a specific mirror.
        """
        BaseConfig.__init__(self, filename)
        self._set_section(mirror)

    @property
    def excludes(self) -> list:
        """
        :return:
            A list of the exclusion patterns for the mirror synchronization --
            the value of the required ``'exclude'`` setting.

        :raises NoOptionError:
            If the setting is absent.
        :raises NoSectionError:
            If the section is absent.
        """
        return self.get_list('exclude')

    @property
    def includes(self) -> list:
        """
        :return:
            A list of the inclusion patterns for the mirror synchronization --
            the value of the required ``'include'`` setting.

        :raises NoOptionError:
            If the setting is absent.
        :raises NoSectionError:
            If the section is absent.
        """
        return self.get_list('include')

    @property
    def mirror_name(self) -> str:
        """
        :return:
            The name of the mirror.

        :raises NoOptionError:
            If the setting is absent.
        :raises NoSectionError:
            If the section is absent.
        """
        return self._get_section()

    @property
    def source(self) -> str:
        """
        :return:
            The source for the mirror synchronization -- the value of the
            required ``'source'`` setting.

        :raises NoOptionError:
            If the setting is absent.
        :raises NoSectionError:
            If the section is absent.
        """
        return self.get('source')

    @property
    def target(self) -> str:
        """
        :return:
            The target for the mirror synchronization -- the value of the
            required ``'target'`` setting.

        :raises NoOptionError:
            If the setting is absent.
        :raises NoSectionError:
            If the section is absent.
        """
        return self.get('target')
