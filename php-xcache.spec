%define		_modname	xcache
%define		_sysconfdir	/etc/php
%define		extensionsdir	%(php-config --extension-dir 2>/dev/null)
Summary:	%{_modname} - PHP opcode cacher
Name:		php-%{_modname}
Version:	1.0
Release:	0.4
License:	BSD
Group:		Development/Languages/PHP
URL:		http://trac.lighttpd.net/xcache/
Source0:	http://210.51.190.228/pub/XCache/Releases/xcache-%{version}.tar.gz
# Source0-md5:	a4e2ff36f16b096f24d3edd9b6ab411b
BuildRequires:	php-devel >= 3:5.0
BuildRequires:	rpmbuild(macros) >= 1.254
BuildRequires:	sed >= 4.0
%{?requires_zend_extension}
Requires:	%{_sysconfdir}/conf.d
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
XCache is a fast, stable PHP opcode cacher that has been tested and is
now running on production servers under high load.

%prep
%setup -q -n xcache

%build
phpize
%configure
%{__make}
%{__sed} -i -e '
	s,zend_extension =.*,zend_extension = %{extensionsdir}/xcache.so,
	s,zend_extension_ts = .*,zend_extension_ts = %{extensionsdir}/xcache.so,
' xcache.ini

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/conf.d

%{__make} install \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install xcache.ini $RPM_BUILD_ROOT%{_sysconfdir}/conf.d/%{_modname}.ini

%clean
rm -rf $RPM_BUILD_ROOT

%post
[ ! -f /etc/apache/conf.d/??_mod_php.conf ] || %service -q apache restart
[ ! -f /etc/httpd/httpd.conf/??_mod_php.conf ] || %service -q httpd restart

%postun
if [ "$1" = 0 ]; then
	[ ! -f /etc/apache/conf.d/??_mod_php.conf ] || %service -q apache restart
	[ ! -f /etc/httpd/httpd.conf/??_mod_php.conf ] || %service -q httpd restart
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS README THANKS
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/conf.d/%{_modname}.ini
%attr(755,root,root) %{extensionsdir}/%{_modname}.so
