Summary:	Shout - Program for feeding MP3 streams to an Icecast server
Summary(pl):	Shout - program dostarczaj±cy strumienie MP3 do serwera Icecast
Name:		shout
Version:	0.8.0
Release:	1
License:	GPL
Group:		Applications/Multimedia
Source0:	http://www.icecast.org/releases/%{name}-%{version}.tar.gz
Source1:	%{name}.init
URL:		http://www.icecast.org/
Prereq:		rc-scripts
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Shout is responsible for feeding a mp3 stream to the Icecast server.

%description -l pl
Shout odpowiada za dostarczanie strumienia mp3 do serwera Icecast.

%prep
%setup -q

%build
CFLAGS="%{rpmcflags}" ./configure --prefix=%{_prefix} --enable-fsstd

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d

%{__make} DESTDIR=$RPM_BUILD_ROOT install

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/shout
install iceplay $RPM_BUILD_ROOT%{_bindir}

mv -f $RPM_BUILD_ROOT%{_sysconfdir}/icecast/shout.conf.dist $RPM_BUILD_ROOT%{_sysconfdir}/icecast/shout.conf

gzip -9nf BUGS BUGS.iceplay CREDITS README.iceplay README.shout TODO *.example

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
	/usr/sbin/useradd -u 57 -r -d /dev/null -s /bin/sh -c "Streamcast" -g icecast icecast 1>&2
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
%defattr(644,root,root,755)
%doc BUGS.gz BUGS.iceplay.gz CREDITS.gz README.iceplay.gz README.shout.gz TODO.gz *.example.gz
%attr(754,root,root) /etc/rc.d/init.d/shout
%attr(640,root,icecast) %config %{_sysconfdir}/icecast/shout.conf
%attr(755,root,root) %{_bindir}/*
