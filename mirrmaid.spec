# vim: foldmethod=marker

%global python_package_name mirrmaid

# These values were arbitrarily chosen so as to be within the range of modern
# (201-999) and legacy (201-499) SYS_UID_MIN/SYS_UID_MAX.
# For a proper Fedora/EPEL package these would require assignment from FPC.
# In our case were exempt from their rules, but also subject to potential,
# eventual breakage, hence a fairly high value but still in a safe range.
# See also:
#   - http://fedoraproject.org/wiki/Packaging:UsersAndGroups
#   - /etc/login.defs for SYS_UID_MIN and SYS_UID_MAX
#   - /usr/share/doc/setup*/uidgid for soft static allocations already
#   assigned by FPC.
%global sys_uid 468
%global sys_gid 468

Name:           mirrmaid
Version:        0.22
Release:        1%{?dist}

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

Requires(pre):  shadow-utils

Requires:       coreutils
Requires:       crontabs
Requires:       python%{python3_pkgversion}
Requires:       python3-doubledog
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

install -d  -m 0755 %{buildroot}%{_var}/lib/%{name}
install -d  -m 0755 %{buildroot}%{_var}/log/%{name}
install -d  -m 0755 %{buildroot}/run/lock/%{name}

install -DP -m 0644 etc/tmpfiles.d/%{name}.conf %{buildroot}%{_sysconfdir}/tmpfiles.d/%{name}.conf
install -Dp -m 0644 etc/%{name}.conf            %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
install -Dp -m 0644 etc/%{name}.cron            %{buildroot}%{_sysconfdir}/cron.d/%{name}
install -Dp -m 0755 bin/%{name}.py              %{buildroot}%{_bindir}/%{name}

%{__python3} lib/setup.py install -O1 --skip-build --root %{buildroot}

# {{{1 clean, pre & post
%clean
rm -rf %{buildroot}

%pre
getent group %{name} >/dev/null || groupadd -f -g %{sys_gid} -r %{name}
if ! getent passwd %{name} >/dev/null
then
    if ! getent passwd %{sys_uid} >/dev/null
    then
        useradd -r -u %{sys_uid} -g %{name} -d /etc/%{name} -s /sbin/nologin \
                -c 'efficient mirror manager' %{name}
    else
        useradd -r -g %{name} -d /etc/%{name} -s /sbin/nologin \
                -c 'efficient mirror manager' %{name}
    fi
fi
exit 0

%post

%preun

%postun

# {{{1 files
%files
%defattr(-,root,root,-)

%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/cron.d/%{name}
%dir %{python3_sitelib}/%{python_package_name}
%doc doc/*
%{_bindir}/%{name}
%{python3_sitelib}/%{python_package_name}/*
%{python3_sitelib}/*egg-info

%defattr(-,%{name},%{name},-)

%{_sysconfdir}/tmpfiles.d/%{name}.conf
%{_var}/lib/%{name}
%{_var}/log/%{name}
/run/lock/%{name}


# {{{1 changelog
%changelog
* Thu Aug 18 2016 John Florian <jflorian@doubledog.org> 0.22-1
- Drop - run-time creation of lock directory (jflorian@doubledog.org)
- Change - location of advisory lock files (jflorian@doubledog.org)
- Change - use soft static user/group account allocation
  (jflorian@doubledog.org)
- Bug - missing Requires(pre) on shadow-utils (jflorian@doubledog.org)
- Change - Python interpreter for Fedora 24 (jflorian@doubledog.org)

* Tue Aug 09 2016 John Florian <jflorian@doubledog.org> 0.21-10
- New - tito releaser for Fedora 24 (jflorian@doubledog.org)

* Sun Jun 26 2016 John Florian <jflorian@doubledog.org> 0.21-9
- Bug - python3-doubledog isn't python34-doubledog for EPEL
  (jflorian@doubledog.org)
- Bug - test releasers don't need git_url (jflorian@doubledog.org)

* Mon Apr 25 2016 John Florian <jflorian@doubledog.org> 0.21-8
- Bug - test targets using wrong releaser (jflorian@doubledog.org)

* Wed Apr 20 2016 John Florian <jflorian@doubledog.org> 0.21-7
- Change - adapt spec for Fedora/EPEL builds (jflorian@doubledog.org)

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
