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
Version:        0.25.1
Release:        2%{?dist}

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
%doc doc/*
%{_bindir}/%{name}
%{python3_sitelib}/%{python_package_name}/*
%{python3_sitelib}/*egg-info

%defattr(-,%{name},%{name},-)

%{_tmpfilesdir}/%{name}.conf
%{_var}/lib/%{name}
%{_var}/log/%{name}
/run/lock/%{name}


# {{{1 changelog
%changelog
* Sun Apr 07 2019 John Florian <jflorian@doubledog.org> 0.25.1-2
- Change - bump for EPEL moving to Python 3.6 (jflorian@doubledog.org)
- New - [tito] test targets per Fedora release (jflorian@doubledog.org)
- Change - [tito] use HTTPS instead of HTTP (jflorian@doubledog.org)
- Drop - [tito] targets for Fedora 27 (jflorian@doubledog.org)

* Mon Nov 19 2018 John Florian <jflorian@doubledog.org> 0.25.1-1
- Bug - cannot import renamed module (jflorian@doubledog.org)

* Fri Nov 16 2018 John Florian <jflorian@doubledog.org> 0.25-1
- New - mirrmaid.conf(5) man page (jflorian@doubledog.org)
- Refactor - mv distutils build into Makefile (jflorian@doubledog.org)
- Refactor - mv setup.py into module (jflorian@doubledog.org)
- Drop - obsolete project tools (jflorian@doubledog.org)
- Janitorial - abbreviate/ensure license in headers (jflorian@doubledog.org)
- Janitorial - distutils should install scripts (jflorian@doubledog.org)
- Bug - Fedora 29 requires newer python3-doubledog (jflorian@doubledog.org)
- New - [PyCharm] codeStyles and scope_settings (jflorian@doubledog.org)
- Change - [PyCharm] bump SDK to Python 3.6 (jflorian@doubledog.org)
- Bug - summary_size incorrectly doc'd in config sample
  (jflorian@doubledog.org)
- New - [tito] targets for Fedora 29 (jflorian@doubledog.org)
- [tito] - restructure epel targets (jflorian@doubledog.org)
- New - [tito] fedora release target (jflorian@doubledog.org)
- Drop - [tito] Fedora 25 release target (jflorian@doubledog.org)
- Drop - [tito] Fedora 25 release target (jflorian@doubledog.org)
- New - [tito] test-all release target (jflorian@doubledog.org)
- Change - [tito] disttag for EL7 (jflorian@doubledog.org)
- New - [tito] targets for Fedora 28 (jflorian@doubledog.org)
- New - [tito] targets for Fedora 27 (jflorian@doubledog.org)
- Bug - [Makefile] queryspec returns partial value (jflorian@doubledog.org)
- New - [Makefile] 'dist' target (jflorian@doubledog.org)
- New - [Makefile] 'clean' target (jflorian@doubledog.org)
- New - [Makefile] vim folding for better organization (jflorian@doubledog.org)
- New - [Makefile] 'help' target (jflorian@doubledog.org)
- Change - [Makefile] don't hide exec of 'git archive' (jflorian@doubledog.org)
- Refactor - [Makefile] rename all vars (jflorian@doubledog.org)
- Drop - [tito] releaser for Fedora 24 (jflorian@doubledog.org)
- New - [tito] releaser for Fedora 26 (jflorian@doubledog.org)
- Drop - [tito] Dart-specific releasers (jflorian@doubledog.org)
- Drop - default defattr directive (jflorian@doubledog.org)
- Drop - tito releaser for Fedora 23 (jflorian@doubledog.org)
- Change - redo of Makefile (jflorian@doubledog.org)
- New - tito release target for Fedora 25 (jflorian@doubledog.org)
- Drop - tito release target for EoL Fedora 22 (jflorian@doubledog.org)

* Wed Nov 02 2016 John Florian <jflorian@doubledog.org> 0.24-1
- Change - log DEBUG/INFO to stdout; rest to stderr (jflorian@doubledog.org)
- Change - adapt to python3-doubledog >= 2.0.0 (jflorian@doubledog.org)
- Change - CLI verbosity options (jflorian@doubledog.org)
- Change - use ArgumentParser instead of OptionParser (jflorian@doubledog.org)
- Bug - FileNotFoundError raised in log rollover (jflorian@doubledog.org)
- Change - move logger instances to class variable (jflorian@doubledog.org)
- Refactor - move .summarizer to .logging.summarizer (jflorian@doubledog.org)
- New - mirrmaid.logging package for Python (jflorian@doubledog.org)
- New - configure logging via external YAML file (jflorian@doubledog.org)
- Janitorial - modernize spec file (jflorian@doubledog.org)
- Refactor - introduce RSYNC constant (jflorian@doubledog.org)
