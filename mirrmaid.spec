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
Version:        0.23
Release:        1%{?dist}

# {{{1 package meta-data
Summary:        efficient mirror manager

Group:          Applications/Internet
Vendor:         doubledog.org
License:        GPLv3+
URL:            http://www.doubledog.org/trac/%{name}/
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python%{python3_pkgversion}-devel

Requires(pre):  shadow-utils

Requires:       coreutils
Requires:       crontabs
Requires:       python%{python3_pkgversion}
Requires:       python3-doubledog
Requires:       rsync
Requires:       util-linux

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

install -d  -m 0755 %{buildroot}%{_var}/lib/%{name}
install -d  -m 0755 %{buildroot}%{_var}/log/%{name}
install -d  -m 0755 %{buildroot}/run/lock/%{name}

install -DP -m 0644 etc/tmpfiles.d/%{name}.conf %{buildroot}%{_sysconfdir}/tmpfiles.d/%{name}.conf
install -Dp -m 0644 etc/%{name}.conf            %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
install -Dp -m 0644 etc/%{name}.cron            %{buildroot}%{_sysconfdir}/cron.d/%{name}
install -Dp -m 0755 bin/%{name}                 %{buildroot}%{_bindir}/%{name}

%{__python3} lib/setup.py install -O1 --skip-build --root %{buildroot}

# {{{1 pre
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
* Tue Sep 13 2016 John Florian <jflorian@doubledog.org> 0.23-1
- Change - Epytext to reStructeredText (jflorian@doubledog.org)
- Janitorial - improve style of longer format() calls (jflorian@doubledog.org)
- Change - simplify SummaryGroup initialization (jflorian@doubledog.org)
- Bug - FileNotFoundError raised in log rollover (jflorian@doubledog.org)
- Refactor - use simpler form of super() calls (jflorian@doubledog.org)
- Refactor - convert summary_due() to property (jflorian@doubledog.org)
- Refactor - convert _summary_body() to property (jflorian@doubledog.org)
- Refactor - convert _reason() to property (jflorian@doubledog.org)
- Refactor - convert __subject() to property (jflorian@doubledog.org)
- Refactor - convert __log_filename() to property (jflorian@doubledog.org)
- Bug - privileges dropped only when both UID/GID are wrong
  (jflorian@doubledog.org)
- Refactor - convert _get_target() to property (jflorian@doubledog.org)
- Refactor - convert _get_source() to property (jflorian@doubledog.org)
- Refactor - convert _get_rsync_options() to property (jflorian@doubledog.org)
- Refactor - convert _get_rsync_includes() to property (jflorian@doubledog.org)
- Refactor - convert _get_rsync_excludes() to property (jflorian@doubledog.org)
- Refactor - convert _get_lock_name() to _lock_name property
  (jflorian@doubledog.org)
- Refactor - use string.format's intrinsic repr() (jflorian@doubledog.org)
- Change - squelch 'module level import not at top of file'
  (jflorian@doubledog.org)
- Change - squelch 'import resolves to its containing file'
  (jflorian@doubledog.org)
- Bug - unresolved reference in format string (jflorian@doubledog.org)
- Bug - unresolved reference 'SynchronizerException' (jflorian@doubledog.org)
- Janitorial - complete project reformat (jflorian@doubledog.org)

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
