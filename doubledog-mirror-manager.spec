%define python_module_name doubledog_mirror_manager

Name:           doubledog-mirror-manager
Version:        0.3
Release:        1%{?dist}
Summary:        doubledog.org local mirror manager

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
Requires:       python-doubledog >= 0.1
Requires:       rsync
Requires:       vixie-cron

%description
This package maintains a synchronized mirror of Fedora resources.

%prep
%setup -q

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}

install -Dp -m 0644 %{name}.cron %{buildroot}%{_sysconfdir}/cron.d/%{name}
install -Dp -m 0644 %{name}.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -Dp -m 0755 %{name} %{buildroot}%{_sbindir}/%{name}

%{__python} setup.py install -O1 --skip-build --root %{buildroot}

%clean
rm -rf %{buildroot}

%post

%preun

%postun

%files
%defattr(-,root,root,-)

%doc AUTHOR COPYING
%{python_sitelib}/%{python_module_name}/*.py
%{python_sitelib}/%{python_module_name}/*.pyc
%{python_sitelib}/%{python_module_name}/*.pyo
%{_sbindir}/%{name}
%{_sysconfdir}/cron.d/%{name}
%{_sysconfdir}/logrotate.d/%{name}


%changelog
* Wed Dec 23 2009 John Florian <jflorian@doubledog.org> - 0.3-1
New - Rewrite in Python for working locking
* Sat Dec 12 2009 John Florian <jflorian@doubledog.org> - 0.2-1
Fix - Mail results
* Sat Dec 12 2009 John Florian <jflorian@doubledog.org> - 0.1-1
New - Initial release
