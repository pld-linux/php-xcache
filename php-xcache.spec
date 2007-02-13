%define		_modname	xcache
Summary:	%{_modname} - PHP opcode cacher
Summary(pl.UTF-8):	%{_modname} - buforowanie opcodów PHP
Name:		php-%{_modname}
Version:	1.2.0
Release:	0.1
License:	BSD
Group:		Development/Languages/PHP
URL:		http://trac.lighttpd.net/xcache/
Source0:	http://210.51.190.228/pub/XCache/rc/1.2.0-rc1/xcache-%{version}-rc1.tar.bz2
# Source0-md5:	a518400a879d8904771867b9f50a650d
BuildRequires:	php-devel >= 3:5.0
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

%build
phpize
%configure
%{__make}
%{__sed} -i -e '
	s,zend_extension =.*,zend_extension = %{php_extensiondir}/xcache.so,
	s,zend_extension_ts = .*,zend_extension_ts = %{php_extensiondir}/xcache.so,
' xcache.ini

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d

%{__make} install \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install xcache.ini $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{_modname}.ini

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
