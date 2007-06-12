%define		_modname	xcache
Summary:	%{_modname} - PHP opcode cacher
Summary(pl.UTF-8):	%{_modname} - buforowanie opcodów PHP
Name:		php-%{_modname}
Version:	1.2.0
Release:	1
License:	BSD
Group:		Development/Languages/PHP
URL:		http://xcache.lighttpd.net/
Source0:	http://210.51.190.228/pub/XCache/Releases/xcache-%{version}.tar.bz2
# Source0-md5:	ffeaa9547037e098d9b041eb9741b51e
Patch0:		xcache-m4.patch
BuildRequires:	php-devel >= 3:5.1
BuildRequires:	rpmbuild(macros) >= 1.344
BuildRequires:	sed >= 4.0
%{?requires_zend_extension}
Requires:	php-common >= 4:5.0.4
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
XCache is a fast, stable PHP opcode cacher that has been tested and is
now running on production servers under high load.

%description -l pl.UTF-8
XCache to szybkie, stabilne buforowanie opcodów PHP, przetestowane i
działające na produkcyjnych serwerach o dużym obciążeniu.

%prep
%setup -q -n xcache
%patch0 -p1
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
install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d

%{__make} install \
	INSTALL_ROOT=$RPM_BUILD_ROOT

# The cache directory where pre-compiled files will reside
install -d $RPM_BUILD_ROOT/var/cache/php-xcache
install -d $RPM_BUILD_ROOT%{_datadir}/xcache

# Drop in the bit of configuration
install xcache.ini $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{_modname}.ini
install -D admin/* $RPM_BUILD_ROOT%{_datadir}/xcache

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS README THANKS
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{_modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{_modname}.so
%{_datadir}/xcache
%dir %attr(775,root,http) /var/cache/php-xcache
