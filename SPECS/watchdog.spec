Summary:          Software and/or Hardware watchdog daemon
Name:             watchdog
Version:          5.16
Release:          1%{?dist}
License:          GPLv2+

URL:              http://sourceforge.net/projects/watchdog/
Source0:          http://downloads.sourceforge.net/watchdog/watchdog-%{version}.tar.gz
Source1:          watchdog.init
Source2:          README.watchdog.ipmi
Source3:          README.Fedora
Source4:          watchdog.service
Source5:          watchdog-ping.service

Patch1:           0001-Choose-libtirpc-or-another-RPC-library-for-XDR-heade.patch
Patch2:           0002-mem-leak-verbose.patch
Patch4:           0004-watchdog-5.13-rhseldoc.patch

BuildRequires:    libtirpc-devel
BuildRequires:    systemd-units

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd


%description
The watchdog program can be used as a powerful software watchdog daemon 
or may be alternately used with a hardware watchdog device such as the 
IPMI hardware watchdog driver interface to a resident Baseboard 
Management Controller (BMC).  watchdog periodically writes to /dev/watchdog; 
the interval between writes to /dev/watchdog is configurable through settings 
in the watchdog sysconfig file.  This configuration file is also used to 
set the watchdog to be used as a hardware watchdog instead of its default 
software watchdog operation.  In either case, if the device is open but not 
written to within the configured time period, the watchdog timer expiration 
will trigger a machine reboot. When operating as a software watchdog, the 
ability to reboot will depend on the state of the machine and interrupts.  
When operating as a hardware watchdog, the machine will experience a hard 
reset (or whatever action was configured to be taken upon watchdog timer 
expiration) initiated by the BMC.

 
%prep
%setup -q -n %{name}-%{version}
%patch1 -p1 -b .xdr-header
%patch2 -p1 -b .verbose
%patch4 -p1 -b .rhseldoc

cp %{SOURCE2} .
cp %{SOURCE3} .
%if 0%{?rhel}
mv README.Fedora README.RHEL
%endif

mv README README.orig
iconv -f ISO-8859-1 -t UTF-8 < README.orig > README


%build
%configure \
    CFLAGS="%{__global_cflags} -I/usr/include/tirpc" \
    LDFLAGS="%{__global_ldflags} -ltirpc"
make %{?_smp_mflags}


%install
install -d -m0755 ${RPM_BUILD_ROOT}%{_sysconfdir}
install -d -m0755 ${RPM_BUILD_ROOT}%{_sysconfdir}/watchdog.d
make DESTDIR=${RPM_BUILD_ROOT} install
install -Dp -m0644 %{name}.sysconfig ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig/watchdog
install -Dp -m0644 %{SOURCE4} ${RPM_BUILD_ROOT}%{_unitdir}/watchdog.service
install -Dp -m0644 %{SOURCE5} ${RPM_BUILD_ROOT}%{_unitdir}/watchdog-ping.service
install -Dd -m0755 ${RPM_BUILD_ROOT}%{_libexecdir}/watchdog/scripts


%post
%systemd_post watchdog.service

%preun 
%systemd_preun watchdog.service
%systemd_preun watchdog.ping.service

%postun 
%systemd_postun_with_restart watchdog.service
%systemd_postun_with_restart watchdog.ping.service

%triggerun -- watchdog < 5.9-4
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply watchdog
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save watchdog >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del watchdog >/dev/null 2>&1 || :
/bin/systemctl try-restart watchdog.service >/dev/null 2>&1 || :
/bin/systemctl try-restart watchdog-ping.service >/dev/null 2>&1 || :


%files
%doc AUTHORS ChangeLog COPYING examples/ IAFA-PACKAGE NEWS README TODO README.watchdog.ipmi
%if 0%{?rhel}
%doc README.RHEL
%else
%doc README.Fedora
%endif
%config(noreplace) %{_sysconfdir}/watchdog.conf
%config(noreplace) %{_sysconfdir}/sysconfig/watchdog
%{_sysconfdir}/watchdog.d
%{_sbindir}/watchdog
%{_sbindir}/wd_identify
%{_sbindir}/wd_keepalive
%{_mandir}/man5/watchdog.conf.5*
%{_mandir}/man8/watchdog.8*
%{_mandir}/man8/wd_identify.8*
%{_mandir}/man8/wd_keepalive.8*
%{_unitdir}/watchdog.service
%{_unitdir}/watchdog-ping.service
%{_libexecdir}/watchdog/scripts


%changelog
* Thu Feb 23 2023 Josef Ridky <jridky@redhat.com> - 5.16-1
- Rebase to version 5.16 (#2149701)

* Wed Apr 21 2021 Than Ngo <than@redhat.com> - 5.15-2
- Resolves: #1846110 - remove deprecated stanza in unit files

* Tue Feb 13 2018 Richard W.M. Jones <rjones@redhat.com> - 5.15-1
- Rebase to watchdog 5.15.
- Remove upstream patches.
- Modify code to use libtirpc.

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 5.13-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 5.13-18
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 5.13-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Mar 06 2017 Josef Ridky <jridky@redhat.com> - 5.13-16
- Scriptlets replaced with new systemd macros (#850364)

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 5.13-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 5.13-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.13-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Aug 21 2014 Kevin Fenzi <kevin@scrye.com> - 5.13-12
- Rebuild for rpm bug 1131960

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.13-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.13-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Nov  7 2013 Ales Ledvinka <aledvink@redhat.com> - 5.13-9
- SELinux: Add /usr/libexec/watchdog/scripts/ for test-bin and repair-bin to inherit from.
- systemd: service with network available dependency
- systemd: correct cgroup for realtime settings
- Document SELinux and systemd.

* Thu Oct 24 2013 Ales Ledvinka <aledvink@redhat.com> - 5.13-5
- SELinux: do not reopen descriptors for reading when only appending.

* Fri Aug  9 2013 Richard W.M. Jones <rjones@redhat.com> - 5.13-4
- Fix License field (software is GPLv2+, not "GPL+").

* Thu Aug  8 2013 Richard W.M. Jones <rjones@redhat.com> - 5.13-3
- Rename README.Fedora to README.RHEL on RHEL.

* Tue Jul 30 2013 Richard W.M. Jones <rjones@redhat.com> - 5.13-2
- Enable /etc/watchdog.d directory for storing test binaries
  (RHBZ#657750, RHBZ#831190).
- Missing BR systemd-units.
- Update .gitignore.
- Drop Group line, not required by modern RPM.

* Thu May 16 2013 Richard W.M. Jones <rjones@redhat.com> - 5.13-1
- New upstream version 5.13.
- Various documentation fixes (RHBZ#948883).

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.12-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.12-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jul 06 2012 Richard W.M. Jones <rjones@redhat.com> - 5.12-1
- New upstream version 5.12 (RHBZ#837949).
- Bring specfile up to modern standards.
- Remove commented sections from previous commit.
- Remove both patches (equivalent changes now upstream).

* Wed Mar 14 2012 Jon Ciesla <limburgher@gmail.com> - 5.9-4
- Migrate to systemd, BZ 661220.

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.9-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 17 2011 Richard W.M. Jones <rjones@redhat.com> - 5.9-1
- New upstream version 5.9 (RHBZ#645541).
- Package new wd_identify program.
- Drop old cleanup patch, most of it is now upstream.
- Add newer cleanup patch, sent upstream.
- Fix some problems with the initscript (RHBZ#523391).
- Add systemd service (file installed but not used) (RHBZ#661220).

* Wed Jan 13 2010 Richard W.M. Jones <rjones@redhat.com> - 5.5-7
- Fix Source0 URL.

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.5-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Mar 13 2009 Richard W.M. Jones <rjones@redhat.com> - 5.5-5
- Updated the cleanup patch and sent upstream.

* Fri Mar 13 2009 Richard W.M. Jones <rjones@redhat.com> - 5.5-3
- Remove dubious "cleanup-nfs" patch.

* Thu Mar  5 2009 Richard W.M. Jones <rjones@redhat.com> - 5.5-2
- Use '-' in defattr line instead of explicit file mode.

* Thu Feb 26 2009 Richard W.M. Jones <rjones@redhat.com> - 5.5-1
- New upstream version 5.5.
- Prepared the package for Fedora review.

* Mon Jun 11  2007 Lon Hohberger <lhh@redhat.com> - 5.3.1-7
- Rebuild for RHEL5 Update 1 - Resolves: 227401

* Wed May 30  2007 Konrad Rzeszutek <konradr@redhat.com> - 5.3.1-6
- Fixed the init script file.

* Tue May 29  2007 Konrad Rzeszutek <konradr@redhat.com> - 5.3.1-5
- Fixed a compile warning in nfsmount_xdr file.

* Wed May 23  2007 Konrad Rzeszutek <konradr@redhat.com> - 5.3.1-4
- Fixed rpmlint warnings.

* Wed May 16  2007 Konrad Rzeszutek <konradr@redhat.com> - 5.3.1-3
- Changes to spec, init script and README file per Carol Hebert recommendation.

* Thu Apr 19  2007 Konrad Rzeszutek <konradr@redhat.com> - 5.3.1-2
- Added README.watchdog.ipmi

* Mon Apr 16  2007 Konrad Rzeszutek <konradr@redhat.com> - 5.3.1-1
- Initial copy. 
