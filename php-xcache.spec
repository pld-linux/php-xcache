%define		modname	xcache
Summary:	%{modname} - PHP opcode cacher
Summary(pl.UTF-8):	%{modname} - buforowanie opcodów PHP
Name:		php-%{modname}
Version:	2.0.1
Release:	1
License:	BSD
Group:		Development/Languages/PHP
URL:		http://xcache.lighttpd.net/
Source0:	http://xcache.lighttpd.net/pub/Releases/%{version}/xcache-%{version}.tar.bz2
# Source0-md5:	d3bc9645dc1b084c1eb45cfc4d8e9ccc
Source1:	%{modname}-apache.conf
Source2:	%{modname}-lighttpd.conf
BuildRequires:	php-devel >= 3:5.1
BuildRequires:	rpmbuild(macros) >= 1.344
BuildRequires:	sed >= 4.0
%{?requires_zend_extension}
Requires:	php-common >= 4:5.0.4
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{modname}
%define		_sysconfdir	%{_webapps}/%{_webapp}
%define		_appdir		%{_datadir}/%{_webapp}

%description
XCache is a fast, stable PHP opcode cacher that has been tested and is
now running on production servers under high load.

%description -l pl.UTF-8
XCache to szybkie, stabilne buforowanie opcodów PHP, przetestowane i
działające na produkcyjnych serwerach o dużym obciążeniu.

%package web
Summary:	WEB interface for xCache
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	webapps
Requires:	webserver(php) >= 5.0

%description web
Via this web interface script you can manage and view statistics of
xCache.

More information you can find at %{url}.

%prep
%setup -q -n %{modname}-%{version}
%{__sed} -i -e '
	s,zend_extension =.*,zend_extension = %{php_extensiondir}/xcache.so,
	s,zend_extension_ts = .*,zend_extension_ts = %{php_extensiondir}/xcache.so,
' xcache.ini

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
install -d $RPM_BUILD_ROOT/var/cache/php-%{modname}
install -d $RPM_BUILD_ROOT%{_appdir}

# Drop in the bit of configuration
cp -p xcache.ini $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
cp -a admin/* $RPM_BUILD_ROOT%{_appdir}

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/lighttpd.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%triggerin web -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun web -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin web -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun web -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerin web -- lighttpd
%webapp_register lighttpd %{_webapp}

%triggerun web -- lighttpd
%webapp_unregister lighttpd %{_webapp}

%files
%defattr(644,root,root,755)
%doc AUTHORS README THANKS
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so

# XXX: what for this dir is used?
%dir %attr(775,root,http) /var/cache/php-xcache

%files web
%defattr(644,root,root,755)
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lighttpd.conf
%{_appdir}
