Summary:	Shout - Program for feeding MP3 streams to an Icecast server
Name:		shout
Version:	0.8.0
Release:	1
URL:		http://www.icecast.org
Source0:	http://www.icecast.org/releases/%{name}-%{version}.tar.gz
Source1:	%{name}.init
License:	GPL
Group:		Applications/Multimedia
Prereq:         rc-scripts
Prereq:         /sbin/chkconfig
Requires(pre):  /bin/id
Requires(pre):  /usr/bin/getgid
Requires(pre):  /usr/sbin/groupadd
Requires(pre):  /usr/sbin/useradd
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Shout is responsible for feeding a mp3 stream to the server.

%prep

%setup -q

%build
CFLAGS="%{rpmcflags}" ./configure --prefix=%{_prefix} --enable-fsstd

# Test if we have a SMP capable computer, and take advantage of it
if [ -x %{_bindir}/getconf ] ; then
  NRPROC=$(%{_bindir}/getconf _NPROCESSORS_ONLN)
   if [ $NRPROC -eq 0 ] ; then
    NRPROC=1
  fi
else
  NRPROC=1
fi

%{__make} -j $NRPROC

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d

%{__make} DESTDIR=$RPM_BUILD_ROOT install

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/shout
install -m755 iceplay $RPM_BUILD_ROOT%{_bindir}
mv $RPM_BUILD_ROOT%{_sysconfdir}/icecast/shout.conf.dist $RPM_BUILD_ROOT%{_sysconfdir}/icecast/shout.conf

strip $RPM_BUILD_ROOT%{_bindir}/* || :

%clean
rm -r $RPM_BUILD_ROOT

%pre
if [ -n "`/usr/bin/getgid icecast`" ]; then
        if [ "`/usr/bin/getgid icecast`" != "57" ]; then
		echo "Warning: group icecast haven't gid=57. Correct this before installing shout." 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -g 57 -r -f icecast
fi
if [ -n "`/bin/id -u icecast 2>/dev/null`" ]; then
	if [ "`/usr/bin/getgid icecast`" != "57" ]; then
		echo "Warning: user icecast haven't uid=57. Correct this before installing shout." 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -u 57 -r -d /dev/null -s /bin/bash -c "Streamcast" -g icecast icecast 1>&2
fi

%post
chkconfig --add shout
if [ -f /var/lock/subsys/shout ]; then
        /etc/rc.d/init.d/shout restart >&2
else
        echo "Run '/etc/rc.d/init.d/shout start' to start shout deamon." >&2
fi
		
%preun
if [ "$1" = "0" ] ; then
        if [ -f /var/lock/subsys/shout ]; then
                /etc/rc.d/init.d/shout stop >&2
        fi
        /sbin/chkconfig --del shout >&2
fi

%files
%defattr(644,icecast,icecast,755)
%doc BUGS BUGS.iceplay CREDITS README.iceplay README.shout TODO *.example
%attr(754,root,icecast) /etc/rc.d/init.d/shout
%attr(640,root,icecast) %config %{_sysconfdir}/icecast/shout.conf
%attr(750,icecast,icecast) %{_bindir}/*
