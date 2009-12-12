Name:           doubledog-mirror-manager
Version:        0.2
Release:        1%{?dist}
Summary:        doubledog.org local mirror manager

Group:          Applications/Internet
Vendor:         doubledog.org
License:        GPLv3+
BuildArch:      noarch
URL:            http://www.doubledog.org/trac/doubledog-mirror-manager/
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:       bash
Requires:       logrotate
Requires:       rsync
Requires:       util-linux-ng
Requires:       vixie-cron

%description
This package maintains a synchronized mirror of Fedora resources.

%prep
%setup -q

%build

%install
rm -rf %{buildroot}

install -Dp -m 0644 %{name}.cron %{buildroot}%{_sysconfdir}/cron.d/%{name}
install -Dp -m 0644 %{name}.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -Dp -m 0755 %{name} %{buildroot}%{_sbindir}/%{name}

%clean
rm -rf %{buildroot}

%post

%preun

%postun

%files
%defattr(-,root,root,-)

%doc AUTHOR COPYING
%{_sbindir}/%{name}
%{_sysconfdir}/cron.d/%{name}
%{_sysconfdir}/logrotate.d/%{name}


%changelog
* Sat Dec 12 2009 John Florian <jflorian@doubledog.org> - 0.2-1
Bug Fix -- Mail Results

Output is supposed to be mailed by default.
* Sat Dec 12 2009 John Florian <jflorian@doubledog.org> - 0.1-1
Initial Release

Package derived from old /Pound/Systems/sbin/rsync-jobs.
