# vim: foldmethod=marker

%global min_py_ver 3.6
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
Version:        0.26.0
Release:        1%{?dist}

# {{{1 package meta-data
Summary:        efficient mirror manager

Group:          Applications/Internet
Vendor:         doubledog.org
License:        GPLv3+
URL:            http://www.doubledog.org/trac/%{name}/
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  pandoc
BuildRequires:  python%{python3_pkgversion}-devel
%if 0%{?rhel} || 0%{?fedora} && 0%{?fedora} < 30
BuildRequires:  systemd
%else
BuildRequires:  systemd-rpm-macros
%endif

Requires(pre):  shadow-utils

Requires:       coreutils
Requires:       crontabs
Requires:       python%{python3_pkgversion} >= %{min_py_ver}
Requires:       python%{python3_pkgversion}-PyYAML
Requires:       python3-doubledog >= 3.0.0, python3-doubledog < 4.0.0
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
make build

# {{{1 install
%install

%{__python3} lib/%{name}/setup.py install -O1 --skip-build --root %{buildroot}

install -d  -m 0755 %{buildroot}%{_var}/lib/%{name}
install -d  -m 0755 %{buildroot}%{_var}/log/%{name}
install -d  -m 0755 %{buildroot}/run/lock/%{name}

install -Dp -m 0644 etc/%{name}.conf            %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
install -Dp -m 0644 etc/%{name}.cron            %{buildroot}%{_sysconfdir}/cron.d/%{name}
install -Dp -m 0644 etc/logging.yaml            %{buildroot}%{_sysconfdir}/%{name}/logging.yaml
install -Dp -m 0644 lib/tmpfiles.d/%{name}.conf %{buildroot}%{_tmpfilesdir}/%{name}.conf

# Install bash-completion facilities.
pushd share/bash-completion
for f in *
do
    install -Dp -m 0644 $f  %{buildroot}%{_datadir}/bash-completion/completions/$f
done
popd

# Compress and install man pages.
pushd share/man/
for section in {1..8}
do
    glob=*.${section}.roff
    if stat -t $glob &> /dev/null
    then
        for page in $glob
        do
            install -dp %{buildroot}/%{_mandir}/man${section}/
            base=$(basename $page .roff)
            gzip < $page > %{buildroot}/%{_mandir}/man${section}/${base}.gz
        done
    fi
done
popd

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

%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/%{name}/logging.yaml
%config(noreplace) %{_sysconfdir}/cron.d/%{name}
%dir %{python3_sitelib}/%{python_package_name}
%doc %{_mandir}/man[1-8]/*.*
%doc CHANGELOG.md README.md
%doc doc/*
%{_bindir}/%{name}
%{_datadir}/bash-completion/completions/
%{python3_sitelib}/%{python_package_name}/*
%{python3_sitelib}/*egg-info

%defattr(-,%{name},%{name},-)

%{_tmpfilesdir}/%{name}.conf
%{_var}/lib/%{name}
%{_var}/log/%{name}
/run/lock/%{name}


# {{{1 changelog
%changelog
* Thu Dec 03 2020 John Florian <jflorian@doubledog.org> 0.26.0-1
- New - [PyCharm] project inspection scope (jflorian@doubledog.org)
- Bug - some failure messages duplicated (jflorian@doubledog.org)
- Change - fail more gracefully if privileges cannot be dropped
  (jflorian@doubledog.org)
- New - --dry-run|-n CLI option (jflorian@doubledog.org)
- New - bash-completion facilities (jflorian@doubledog.org)
- New - README.md (jflorian@doubledog.org)
- New - mirrmaid(1) man page (jflorian@doubledog.org)
- New - MirrmaidCLI class (jflorian@doubledog.org)
- Change - [PyCharm] upgrade caused config schema (jflorian@doubledog.org)
- New - max_workers config opt to limit concurrency (jflorian@doubledog.org)
- Refactor - replace str.format() with f-string literals
  (jflorian@doubledog.org)
- Bug - rsync orphans after stop/kill (jflorian@doubledog.org)
- New - Synchronizer.stop method (jflorian@doubledog.org)
- New - Synchronizer._subprocess field (jflorian@doubledog.org)
- Change - defer log formatting to logging system (jflorian@doubledog.org)
- Janitorial - global code reformat (jflorian@doubledog.org)
- Change - Synchronizer now subclasses Thread (jflorian@doubledog.org)
- Janitorial - indent yaml by 2 not 4 (jflorian@doubledog.org)
- Refactor - rename property Synchronizer._source (jflorian@doubledog.org)
- Refactor - rename property Synchronizer._target (jflorian@doubledog.org)
- Change - [PyCharm] squelch PEP8 naming convention violation
  (jflorian@doubledog.org)
- Bug - incorrect return type annotation (jflorian@doubledog.org)
- New - formal CHANGELOG (jflorian@doubledog.org)
- Change - [PyCharm] bump SDK to Python 3.8 (jflorian@doubledog.org)
- New - [tito] targets for Fedora 33 (jflorian@doubledog.org)
- Drop - [tito] targets for Fedora 30 (jflorian@doubledog.org)
- New - [tito] targets for Fedora 32 (jflorian@doubledog.org)
- Drop - [tito] targets for Fedora 29 (jflorian@doubledog.org)
- New - [tito] targets for CentOS 8 (jflorian@doubledog.org)
- New - [tito] targets for Fedora 31 (jflorian@doubledog.org)

* Fri Sep 27 2019 John Florian <jflorian@doubledog.org> 0.25.1-3
- Bug - [spec] systemd-tmpfiles s/b under /usr not /etc
  (jflorian@doubledog.org)
- Drop - [tito] targets for Fedora 28 (jflorian@doubledog.org)
- New - [tito] targets for Fedora 30 (jflorian@doubledog.org)

* Sun Apr 07 2019 John Florian <jflorian@doubledog.org> 0.25.1-2
- Change - bump for EPEL moving to Python 3.6 (jflorian@doubledog.org)
- New - [tito] test targets per Fedora release (jflorian@doubledog.org)
- Change - [tito] use HTTPS instead of HTTP (jflorian@doubledog.org)
- Drop - [tito] targets for Fedora 27 (jflorian@doubledog.org)
