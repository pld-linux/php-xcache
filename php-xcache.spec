%define		_modname	xcache
Summary:	%{_modname} - PHP opcode cacher
Summary(pl.UTF-8):	%{_modname} - buforowanie opcodów PHP
Name:		php-%{_modname}
Version:	1.2.1
Release:	2
License:	BSD
Group:		Development/Languages/PHP
URL:		http://xcache.lighttpd.net/
Source0:	http://xcache.lighttpd.net/pub/Releases/1.2.1/xcache-%{version}.tar.bz2
# Source0-md5:	42133468871c573c397b8375dc8c19b6
BuildRequires:	php-devel >= 3:5.1
BuildRequires:	rpmbuild(macros) >= 1.344
BuildRequires:	sed >= 4.0
%{?requires_zend_extension}
Requires:	php-common >= 4:5.0.4
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		xcache
%define		_sysconfdir	%{_webapps}/%{_webapp}
%define		_appdir		%{_datadir}/%{_webapp}

%description
XCache is a fast, stable PHP opcode cacher that has been tested and is
now running on production servers under high load.

%description -l pl.UTF-8
XCache to szybkie, stabilne buforowanie opcodów PHP, przetestowane i
działające na produkcyjnych serwerach o dużym obciążeniu.

%prep
%setup -q -n xcache-%{version}
%{__sed} -i -e '
	s,zend_extension =.*,zend_extension = %{php_extensiondir}/xcache.so,
	s,zend_extension_ts = .*,zend_extension_ts = %{php_extensiondir}/xcache.so,
' xcache.ini

cat > apache.conf <<'EOF'
Alias /xcache %{_appdir}
<Directory %{_appdir}>
	Allow from 127.0.0.1
</Directory>
EOF

%build
phpize
%configure \
	--enable-xcache \
	--enable-xcache-optimizer \
	--enable-xcache-coverager
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{php_sysconfdir}/conf.d,%{_sysconfdir}}

%{__make} install \
	INSTALL_ROOT=$RPM_BUILD_ROOT

# The cache directory where pre-compiled files will reside
install -d $RPM_BUILD_ROOT/var/cache/php-xcache
install -d $RPM_BUILD_ROOT%{_appdir}

# Drop in the bit of configuration
install xcache.ini $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{_modname}.ini
install admin/* $RPM_BUILD_ROOT%{_appdir}

install apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
install apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%files
%defattr(644,root,root,755)
%doc AUTHORS README THANKS
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{_modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{_modname}.so
%{_appdir}
%dir %attr(775,root,http) /var/cache/php-xcache
