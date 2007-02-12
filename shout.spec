Summary:	Shout - Program for feeding MP3 streams to an Icecast server
Summary(pl.UTF-8):	Shout - program dostarczający strumienie MP3 do serwera Icecast
Summary(pt_BR.UTF-8):	Ferramenta de broadcast de MP3 para o Icecast
Name:		shout
Version:	0.8.0
Release:	3
License:	GPL
Group:		Applications/Sound
Source0:	http://www.icecast.org/releases/%{name}-%{version}.tar.gz
# Source0-md5:	d44604a2235532e31e10d2d0e4740f20
Source1:	%{name}.init
URL:		http://www.icecast.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	rpmbuild(macros) >= 1.202
PreReq:		rc-scripts
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Provides:	group(icecast)
Provides:	user(icecast)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Shout is a broadcasting tool for icecast streaming servers. It
broadcasts MP3 files to an icecast server, and supports external
programs which do song selection.

%description -l pl.UTF-8
Shout odpowiada za dostarczanie strumienia MP3 do serwera Icecast.

%description -l pt_BR.UTF-8
Ferramenta de broadcast para servidores de streaming icecast. Faz
broadcast de arquivos MP3 para um servidor icecast e suporta programas
externos para seleção das músicas.

%prep
%setup -q

%build
rm -f sock.o
cp -f /usr/share/automake/config.* .
%{__aclocal}
%{__autoconf}
%configure \
	--enable-fsstd

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/shout
install iceplay $RPM_BUILD_ROOT%{_bindir}

mv -f $RPM_BUILD_ROOT%{_sysconfdir}/icecast/shout.conf.dist $RPM_BUILD_ROOT%{_sysconfdir}/icecast/shout.conf

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 57 icecast
%useradd -u 57 -r -d /usr/share/empty -s /bin/false -c "Streamcast" -g icecast icecast

%post
/sbin/chkconfig --add shout
if [ -f /var/lock/subsys/shout ]; then
	/etc/rc.d/init.d/shout restart >&2
else
	echo "Run '/etc/rc.d/init.d/shout start' to start shout daemon." >&2
fi

%preun
if [ "$1" = "0" ] ; then
	if [ -f /var/lock/subsys/shout ]; then
		/etc/rc.d/init.d/shout stop >&2
	fi
	/sbin/chkconfig --del shout >&2
fi

%postun
if [ "$1" = "0" ]; then
	%userremove icecast
	%groupremove icecast
fi

%files
%defattr(644,root,root,755)
%doc BUGS BUGS.iceplay CREDITS README.iceplay README.shout TODO *.example
%attr(754,root,root) /etc/rc.d/init.d/shout
%attr(640,root,icecast) %config %{_sysconfdir}/icecast/shout.conf
%attr(755,root,root) %{_bindir}/*
