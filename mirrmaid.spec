%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

%define python_module_name mirrmaid

Name:           mirrmaid
Version:        0.6
Release:        2%{?dist}
Summary:        efficient mirror manager

Group:          Applications/Internet
Vendor:         doubledog.org
License:        GPLv3+
BuildArch:      noarch
URL:            http://www.doubledog.org/trac/%{name}/
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python-devel
Requires:       logrotate
Requires:       python >= 2.6
Requires:       python-doubledog >= 0.4
Requires:       rsync
Requires:       vixie-cron

%description
This package efficiently maintains synchronized local mirrors of remote
resources.  This is primarly accomplished by a sophisticated wrapper around
the venerable rsync package.  The primary advantage of this package over rsync
is the simple yet powerful configuration, automatic cron scheduling and
locking to prevent concurrently running instances from working against each
other.

%prep
%setup -q

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}

install -d  -m 0755                     %{buildroot}%{_var}/log/%{name}
install -Dp -m 0644 %{name}.conf        %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
install -Dp -m 0644 %{name}.cron        %{buildroot}%{_sysconfdir}/cron.d/%{name}
install -Dp -m 0644 %{name}.logrotate   %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -Dp -m 0755 %{name}.py          %{buildroot}%{_sbindir}/%{name}

%{__python} setup.py install -O1 --skip-build --root %{buildroot}

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

%doc AUTHOR COPYING
%{python_sitelib}/%{python_module_name}*.egg-info
%{python_sitelib}/%{python_module_name}/*.py
%{python_sitelib}/%{python_module_name}/*.pyc
%{python_sitelib}/%{python_module_name}/*.pyo
%{_sbindir}/%{name}
%{_sysconfdir}/cron.d/%{name}
%{_sysconfdir}/logrotate.d/%{name}
%{_sysconfdir}/%{name}/%{name}.conf

%defattr(-,%{name},%{name},-)
%{_var}/log/%{name}


%changelog
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
