# TODO
# - verify %lang codes
#
# Conditional build:
%bcond_without	web		# make web package

# build "web" only for 5.5 version
%if 0%{?_pld_builder:1} && "%{?php_suffix}" != "55"
%undefine	with_web
%endif

%define		php_name	php%{?php_suffix}
%define		modname	xcache
Summary:	%{modname} - PHP opcode cacher
Summary(pl.UTF-8):	%{modname} - buforowanie opcodów PHP
Name:		%{php_name}-%{modname}
Version:	3.2.0
Release:	1
License:	BSD
Group:		Development/Languages/PHP
Source0:	http://xcache.lighttpd.net/pub/Releases/%{version}/xcache-%{version}.tar.bz2
# Source0-md5:	3655bd20483dc23d24f87f9dc924a62e
Source1:	%{modname}-apache.conf
Source2:	%{modname}-lighttpd.conf
Patch0:		config.patch
Patch1:		ini-settings.patch
URL:		http://xcache.lighttpd.net/
BuildRequires:	%{php_name}-devel >= 4:5.2.17-8
BuildRequires:	rpmbuild(macros) >= 1.344
BuildRequires:	sed >= 4.0
%{?requires_zend_extension}
Requires:	php(core) >= 5.0.4
Requires(triggerpostun):	sed >= 4.0
Provides:	php(xcache) = %{version}
Obsoletes:	php-xcache < 3.1.0-3
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

%package -n php-xcache-web
Summary:	WEB interface for xCache
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	webapps
Requires:	webserver(access)
Requires:	webserver(php) >= 5.0
Obsoletes:	php55-xcache-web < 3.1.0-5
%if "%{_rpmversion}" >= "5"
BuildArch:	noarch
%endif

%description -n php-xcache-web
Via this web interface script you can manage and view statistics of
xCache.

More information you can find at %{url}.

%prep
%setup -q -n %{modname}-%{version}
%patch0 -p1
%patch1 -p1
%{__sed} -i.bak -e '
	s,@extensiondir@,%{php_extensiondir},
' xcache.ini

mv htdocs/config{.default,}.php
mv htdocs/config.example.php config.example.php
mv htdocs/cacher/config{.default,}.php
mv htdocs/cacher/config.example.php cacher.config.example.php
mv htdocs/coverager/config{.default,}.php
mv htdocs/coverager/config.example.php coverager.config.example.php

%{__rm} htdocs/common/lang/*.po
%{__rm} htdocs/coverager/lang/*.po
%{__rm} htdocs/cacher/lang/*.po

# wtf?
%{__rm} htdocs/diagnosis/lang/zh-tranditional.php

%build
phpize
%configure \
	--enable-xcache \
	--enable-xcache-optimizer \
	--enable-xcache-coverager
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cp -p xcache.ini $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini

# The cache directory where pre-compiled files will reside
install -d $RPM_BUILD_ROOT/var/cache/php-%{modname}

%if %{with web}
install -d $RPM_BUILD_ROOT{%{_appdir},%{_sysconfdir}}
cp -a htdocs/* $RPM_BUILD_ROOT%{_appdir}
%{__rm} $RPM_BUILD_ROOT%{_appdir}/diagnosis/lang/*.po

mv $RPM_BUILD_ROOT{%{_appdir},%{_sysconfdir}}/config.php
mv $RPM_BUILD_ROOT{%{_appdir}/cacher/config.php,%{_sysconfdir}/cacher.config.php}
mv $RPM_BUILD_ROOT{%{_appdir}/coverager/config.php,%{_sysconfdir}/coverager.config.php}
ln -s %{_sysconfdir}/config.php $RPM_BUILD_ROOT%{_appdir}/config.php
ln -s %{_sysconfdir}/cacher.config.php $RPM_BUILD_ROOT%{_appdir}/cacher/config.php
ln -s %{_sysconfdir}/coverager.config.php $RPM_BUILD_ROOT%{_appdir}/coverager/config.php
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/lighttpd.conf
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%triggerpostun -- %{name} < 3.0.0-0.8
%{__sed} -i -e 's,zend_extension,extension,' %{php_sysconfdir}/conf.d/%{modname}.ini

%triggerin -n php-xcache-web -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -n php-xcache-web -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -n php-xcache-web -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -n php-xcache-web -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerin -n php-xcache-web -- lighttpd
%webapp_register lighttpd %{_webapp}

%triggerun -n php-xcache-web -- lighttpd
%webapp_unregister lighttpd %{_webapp}

%files
%defattr(644,root,root,755)
%doc AUTHORS README THANKS
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so

# XXX: what for this dir is used?
%dir %attr(775,root,http) /var/cache/php-xcache

%if %{with web}
%files -n php-xcache-web
%defattr(644,root,root,755)
%doc config*.example.php
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lighttpd.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/config.php
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/cacher.config.php
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/coverager.config.php
%dir %{_appdir}
%{_appdir}/*.php

%dir %{_appdir}/common
%{_appdir}/common/*.css
%{_appdir}/common/*.js
%{_appdir}/common/*.php
%{_appdir}/common/*.png
%dir %{_appdir}/common/lang
%{_appdir}/common/lang/en.php
%lang(cn) %{_appdir}/common/lang/zh-simplified.php
%lang(cn) %{_appdir}/common/lang/zh-traditional.php

%dir %{_appdir}/cacher
%{_appdir}/cacher/*.css
%{_appdir}/cacher/*.php
%{_appdir}/cacher/sub
%dir %{_appdir}/cacher/lang
%{_appdir}/cacher/lang/en.php
%lang(zh_CN) %{_appdir}/cacher/lang/zh-simplified.php
%lang(zh_CN) %{_appdir}/cacher/lang/zh-traditional.php

%dir %{_appdir}/coverager
%{_appdir}/coverager/*.css
%{_appdir}/coverager/*.php
%dir %{_appdir}/coverager/lang
%{_appdir}/coverager/lang/en.php
%lang(zh_CN) %{_appdir}/coverager/lang/zh-simplified.php
%lang(zh_CN) %{_appdir}/coverager/lang/zh-traditional.php

%dir %{_appdir}/diagnosis
%{_appdir}/diagnosis/*.css
%{_appdir}/diagnosis/*.php
%dir %{_appdir}/diagnosis/lang
%{_appdir}/diagnosis/lang/en.php
%lang(zh_CN) %{_appdir}/diagnosis/lang/zh-simplified.php
%lang(zh_CN) %{_appdir}/diagnosis/lang/zh-traditional.php
%endif
