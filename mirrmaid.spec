%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

%define python_module_name mirrmaid

Name:           mirrmaid
Version:        0.12
Release:        1%{?dist}
Summary:        efficient mirror manager

Group:          Applications/Internet
Vendor:         doubledog.org
License:        GPLv3+
BuildArch:      noarch
URL:            http://www.doubledog.org/trac/%{name}/
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python-devel
Requires:       coreutils
Requires:       logrotate
Requires:       python >= 2.6
Requires:       python3-doubledog >= 1.1
Requires:       rsync
Requires:       util-linux-ng
Requires:       vixie-cron

%description
This package efficiently maintains synchronized target mirrors of source
resources.  This is primarily accomplished by a sophisticated wrapper around
the venerable rsync package.  The primary advantage of this package over rsync
is the simple yet powerful configuration, automatic cron scheduling and
locking to prevent concurrently running instances from working against each
other.

%prep
%setup -q

%build
%{__python} pkg_tools/setup.py build

%install
rm -rf %{buildroot}

install -Dp -m 0644 etc/%{name}.conf            %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
install -Dp -m 0644 etc/%{name}.cron            %{buildroot}%{_sysconfdir}/cron.d/%{name}
install -Dp -m 0644 etc/%{name}.logrotate       %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -Dp -m 0755 bin/%{name}.py              %{buildroot}%{_bindir}/%{name}
install -d  -m 0755                             %{buildroot}%{_var}/log/%{name}

%{__python} pkg_tools/setup.py install -O1 --skip-build --root %{buildroot}

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

%files
%defattr(-,root,root,-)

%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/cron.d/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%doc doc/AUTHOR
%doc doc/COPYING
%{_bindir}/%{name}
%{python_sitelib}/%{python_module_name}*.egg-info
%{python_sitelib}/%{python_module_name}/*.py
%{python_sitelib}/%{python_module_name}/*.pyc
%{python_sitelib}/%{python_module_name}/*.pyo

%defattr(-,%{name},%{name},-)
%{_var}/log/%{name}


%changelog
* Tue Oct 11 2011 John Florian <john_florian@dart.biz> - 0.12-1
Fix - quoting error in manager
Janitorial - PEP-8 conformance
Refactor - simplify boolean ops
* Mon Oct 10 2011 John Florian <jflorian@doubledog.org> - 0.11-1
Fix - fails with lock on tmpfs and net user account
Fix - no copyright variable in modules
Fix - shouldn't use env to find python
Fix - test harness mishandles quoted args
Janitorial - complete project reorg
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
