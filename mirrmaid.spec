# vim: foldmethod=marker

%global python_package_name mirrmaid

# {{{1 package meta-data
Name:           mirrmaid
Version:        0.20
Release:        1%{?dist}
Summary:        efficient mirror manager

Group:          Applications/Internet
Vendor:         doubledog.org
License:        GPLv3+
URL:            http://www.doubledog.org/trac/%{name}/
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python3-devel
Requires:       coreutils
Requires:       crontabs
Requires:       python3 >= 3
Requires:       python3-doubledog >= 1.3
Requires:       rsync
Requires:       util-linux-ng

%description
This package efficiently maintains synchronized target mirrors of source
resources.  This is primarily accomplished by a sophisticated wrapper around
the venerable rsync package.  The primary advantage of this package over rsync
is the simple yet powerful configuration, automatic cron scheduling and
locking to prevent concurrently running instances from working against each
other.

# {{{1 prep & build
%prep
%setup -q

%build
%{__python3} lib/setup.py build

# {{{1 install
%install
rm -rf %{buildroot}

install -Dp -m 0644 etc/%{name}.conf            %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
install -Dp -m 0644 etc/%{name}.cron            %{buildroot}%{_sysconfdir}/cron.d/%{name}
install -Dp -m 0755 bin/%{name}.py              %{buildroot}%{_bindir}/%{name}
install -d  -m 0755                             %{buildroot}%{_var}/lib/%{name}
install -d  -m 0755                             %{buildroot}%{_var}/log/%{name}

%{__python3} lib/setup.py install -O1 --skip-build --root %{buildroot}

# {{{1 clean, pre & post
%clean
rm -rf %{buildroot}

%pre
if ! getent group %{name}
then
    groupadd -r %{name}
fi
if ! getent passwd %{name}
then
    useradd -d /etc/%{name} -g %{name} -M -r %{name}
fi

%post

%preun

%postun

# {{{1 files
%files
%defattr(-,root,root,-)

%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/cron.d/%{name}
%doc doc/*
%{_bindir}/%{name}

%dir %{python3_sitelib}/%{python_package_name}
%{python3_sitelib}/%{python_package_name}/*
%{python3_sitelib}/*egg-info

%defattr(-,%{name},%{name},-)
%{_var}/lib/%{name}
%{_var}/log/%{name}


# {{{1 changelog
%changelog
* Sat Jul 12 2014 John Florian <jflorian@doubledog.org> - 0.20-1
 - Fix - correct releasers config (jflorian@doubledog.org)
 - Initialized to use tito. (john_florian@dart.biz)
 - Change - default configuration improvements (john_florian@dart.biz)
 - Change - quote values smartly, using repr() (john_florian@dart.biz)
 - Janitorial - code format (john_florian@dart.biz)
 - Janitorial - documentation improvements (john_florian@dart.biz)
 - Fix - ConnectionError exception is unhandled (john_florian@dart.biz)
 - Fix - spelling (john_florian@dart.biz)
 - Refactor - 'exit' shadows built-in name (john_florian@dart.biz)
 - Janitorial - PEP-8 conformance (john_florian@dart.biz)
 - Fix - no encoding specified for files (john_florian@dart.biz)
 - Refactor - methods may be static (john_florian@dart.biz)
 - Refactor - argument equals default value (john_florian@dart.biz)
 - Janitorial - reformat project (john_florian@dart.biz)

* Tue Jun 24 2014 John Florian <john_florian@dart.biz> - 0.19-1
 - Change - global macro preferred over define in spec (john_florian@dart.biz)
 - Fix - inaccurate terminology (john_florian@dart.biz)
 - New - vim folding markers in spec (john_florian@dart.biz)
 - Change - PyCharm prefers setup.py with lib/ (john_florian@dart.biz)

* Sun Jan 05 2014 John Florian <jflorian@doubledog.org> - 0.18-1
Janitorial - update copyrights
* Mon Dec 24 2012 John Florian <jflorian@doubledog.org> - 0.17-1
Change - sanitize Python environment
New - drop privileges at startup
New - notification summarizes reason
New - proxy support
Refactor - introduce _log_environment()
Refactor - introduce _run()
* Mon Nov 26 2012 John Florian <jflorian@doubledog.org> - 0.16-1
Fix - some MTAs may require sender's domain
* Sat Nov 24 2012 John Florian <jflorian@doubledog.org> - 0.15-1
Change - simplify logging hierarchy
Fix - summary log must be unique to summary_group
Refactor - replace all formatting with new style
Refactor - simplify format() specifications
* Mon Nov 19 2012 John Florian <jflorian@doubledog.org> - 0.14-1
New - grouping/splitting of operations summaries
* Sun Nov 18 2012 John Florian <jflorian@doubledog.org> - 0.13-1
Python 3 Implementation:
    Change - launch with correct interpreter
    Change - revise spec for Python 3 packaging
    Refactor - make compatible with python3-doubledog
    Refactor - use Python 3 exception syntax

Feature enhancements:
    New - log summarization feature
    Change - make operations summaries configurable
    Change - rsync stderr now logged as ERROR
    Change - utilize AsynchronousStreamingSubprocess
    New - debug logging of environment settings
    Drop - logrotate configuration

Bug Fixes:
    Fix - spelling errors / improve comments
    Fix - use of eval() is a security risk

Other Cleanup:
    Change - simplify python packaging
    Janitorial - ignore valid broad Exception
    Janitorial - optimize imports
    Janitorial - update copyrights
    New - copyright_update configuration
    Refactor - implement @property decorators in config
    Refactor - introduce new exceptions module
    Refactor - rename Mirror_Config to MirrorConfig
    Refactor - rename Mirror_Manager to MirrorManager
    Refactor - rename Mirrors_Config to MirrorsConfig
    Refactor - rename Synchronizer_Exception to SynchronizerException
* Tue Oct 11 2011 John Florian <john_florian@dart.biz> - 0.12-1
Fix - quoting error in manager
Janitorial - PEP-8 conformance
Refactor - simplify boolean ops
* Mon Oct 10 2011 John Florian <jflorian@doubledog.org> - 0.11-1
Fix - fails with lock on tmpfs and net user account
Fix - no copyright variable in modules
Fix - shouldn't use env to find python
Fix - test harness mishandles quoted args
Janitorial - complete project reorganization
Janitorial - remove trailing whitespace
Janitorial - use standard Python quoting style
* Fri Jul 23 2010 John Florian <john_florian@dart.biz> - 0.9-1
Fix - config files overwritten on upgrade
Fix - cron job should be disabled by default
Fix - Invalid_Configuration exceptions uncaught
Fix - mirrmaid should not be installed in /usr/sbin
Fix - should run as a nice process
New - support for inclusion patterns
* Tue Jun 08 2010 John Florian <jflorian@doubledog.org> - 0.8-1
Fix - assumes remote==source and local==target
Fix - default conf should be benign
* Fri Jun 04 2010 John Florian <jflorian@doubledog.org> - 0.7-1
Fix - lock dir not writable by non-root user
Fix - log file not writable by non-root user
* Fri Jun 04 2010 John Florian <jflorian@doubledog.org> - 0.6-2
Fix - detection of user acct not LDAP-friendly
* Fri Jun 04 2010 John Florian <jflorian@doubledog.org> - 0.6-1
Change - add license headers to prominent files
Change - renaming project to mirrmaid
Fix - should not be running as root
Fix - usage OS standard exit values
* Sun Jan 03 2010 John Florian <jflorian@doubledog.org> - 0.5-1
Change - Use new Lock_File
New - Allow overriding of config file path
* Sun Dec 27 2009 John Florian <jflorian@doubledog.org> - 0.4-1
Fix - pipe to rsync not handled correctly
* Wed Dec 23 2009 John Florian <jflorian@doubledog.org> - 0.3-1
New - complete rewrite, now in Python
* Sat Dec 12 2009 John Florian <jflorian@doubledog.org> - 0.2-1
Fix - Mail results
* Sat Dec 12 2009 John Florian <jflorian@doubledog.org> - 0.1-1
New - Initial release
