# vim: foldmethod=marker

%global python_package_name mirrmaid

Name:           mirrmaid
Version:        0.21
Release:        6%{?dist}

# {{{1 package meta-data
Summary:        efficient mirror manager

Group:          Applications/Internet
Vendor:         doubledog.org
License:        GPLv3+
URL:            http://www.doubledog.org/trac/%{name}/
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python%{python3_pkgversion}-devel

Requires:       coreutils
Requires:       crontabs
Requires:       python%{python3_pkgversion}
Requires:       python%{python3_pkgversion}-doubledog
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
* Wed Apr 20 2016 John Florian <jflorian@doubledog.org> 0.21-6
- Change - several tito configuration issues (jflorian@doubledog.org)

* Mon Mar 07 2016 John Florian <jflorian@doubledog.org> 0.21-5
- Janitorial - update copyrights (jflorian@doubledog.org)
- Change - redo tito config for koji (jflorian@doubledog.org)
- Change - rename tito's subdir (jflorian@doubledog.org)

* Tue Jul 07 2015 John Florian <jflorian@doubledog.org> 0.21-4
- New - f22 target for Koji at Dart (jflorian@doubledog.org)

* Mon May 11 2015 John Florian <john_florian@dart.biz> 0.21-3
- New - f21 target for Koji at Dart (john_florian@dart.biz)

* Wed May 06 2015 John Florian <jflorian@doubledog.org> 0.21-2
 - Change - use ReleaseTagger instead of VersionTagger (jflorian@doubledog.org)
 - New - "koji" and "koji-dart" release targets (jflorian@doubledog.org)

* Fri Feb 27 2015 John Florian <jflorian@doubledog.org> - 0.21-1
 - Janitorial - update Copyrights (jflorian@doubledog.org)
 - New - Fedora 21 release targets (jflorian@doubledog.org)
 - Change - new packaging requirements for cron jobs (jflorian@doubledog.org)
 - New - optimized tito releaser configuration (jflorian@doubledog.org)

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
