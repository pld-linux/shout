Summary:	Shout - Program for feeding MP3 streams to an Icecast server
Summary(pl):	Shout - program dostarczaj±cy strumienie MP3 do serwera Icecast
Summary(pt_BR):	Ferramenta de broadcast de MP3 para o Icecast
Name:		shout
Version:	0.8.0
Release:	2
License:	GPL
Group:		Applications/Sound
Source0:	http://www.icecast.org/releases/%{name}-%{version}.tar.gz
Source1:	%{name}.init
URL:		http://www.icecast.org/
BuildRequires:	autoconf
BuildRequires:	automake
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Prereq:		rc-scripts
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Shout is a broadcasting tool for icecast streaming servers. It
broadcasts mp3 files to an icecast server, and supports external
programs which do song selection.

%description -l pl
Shout odpowiada za dostarczanie strumienia mp3 do serwera Icecast.

%description -l pt_BR
Ferramenta de broadcast para servidores de streaming icecast. Faz
broadcast de arquivos mp3 para um servidor icecast e suporta programas
externos para seleção das músicas.

%prep
%setup -q

%build
rm -f sock.o
cp -f /usr/share/automake/config.* .
aclocal
%{__autoconf}
%configure \
	--enable-fsstd

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d

%{__make} DESTDIR=$RPM_BUILD_ROOT install

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/shout
install iceplay $RPM_BUILD_ROOT%{_bindir}

mv -f $RPM_BUILD_ROOT%{_sysconfdir}/icecast/shout.conf.dist $RPM_BUILD_ROOT%{_sysconfdir}/icecast/shout.conf

%clean
rm -r $RPM_BUILD_ROOT

%pre
if [ -n "`/usr/bin/getgid icecast`" ]; then
        if [ "`/usr/bin/getgid icecast`" != "57" ]; then
		echo "Error: group icecast doesn't have gid=57. Correct this before installing shout." 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -g 57 -r -f icecast
fi
if [ -n "`/bin/id -u icecast 2>/dev/null`" ]; then
	if [ "`/usr/bin/getgid icecast`" != "57" ]; then
		echo "Error: user icecast doesn't have uid=57. Correct this before installing shout." 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -u 57 -r -d /dev/null -s /bin/false -c "Streamcast" -g icecast icecast 1>&2
fi

%post
/sbin/chkconfig --add shout
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
%doc BUGS BUGS.iceplay CREDITS README.iceplay README.shout TODO *.example
%attr(754,root,root) /etc/rc.d/init.d/shout
%attr(640,root,icecast) %config %{_sysconfdir}/icecast/shout.conf
%attr(755,root,root) %{_bindir}/*
