#
# Conditional build:
%bcond_with	tests	# py.test tests [require ptys, so not on builders]
%bcond_without	doc	# Sphinx documentation

%define		module	pexpect
Summary:	Pure Python Expect-like module
Summary(pl.UTF-8):	Moduł podobny do narzędzia Expect napisany w czystym Pythonie
Name:		python3-%{module}
Version:	4.9.0
Release:	1
License:	ISC
Group:		Development/Languages/Python
#Source0Download: https://pypi.org/simple/pexpect/
Source0:	https://files.pythonhosted.org/packages/source/p/pexpect/pexpect-%{version}.tar.gz
# Source0-md5:	f48d48325ee7f1221add0396ea9e2f14
Patch0:		pexpect-use_setuptools.patch
URL:		https://pexpect.readthedocs.io/
%if %{with tests} && %(locale -a | grep -q '^C\.utf8$'; echo $?)
BuildRequires:	glibc-localedb-all
%endif
BuildRequires:	python3-modules >= 1:3.2
BuildRequires:	python3-setuptools
%if %{with tests}
BuildRequires:	python3-ptyprocess >= 0.5
BuildRequires:	python3-pytest
%endif
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.714
%if %{with doc}
BuildRequires:	python3-sphinxcontrib_github_alt
BuildRequires:	sphinx-pdg-3
%endif
Requires:	python3-modules >= 1:3.2
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Pexpect is a pure Python module for spawning child applications;
controlling them; and responding to expected patterns in their output.
Pexpect works like Don Libes' Expect. Pexpect allows your script to
spawn a child application and control it as if a human were typing
commands.

%description -l pl.UTF-8
Pexpect jest modułem napisanym wyłącznie w Pythonie przeznaczonym do
uruchamiania aplikacji i kontroli nad nimi poprzez reagowanie na
znalezione wzorce na ich wyjściu. Pexpect działa podobnie do Expecta
Dona Libesa - pozwala skryptom z ich poziomu uruchomić inne programy i
sprawować nad nimi kontrolę imitując interakcję użytkownika.

%package apidocs
Summary:	Documentation for Python pexpect module
Summary(pl.UTF-8):	Dokumentacja do modułu Pythona pexpect
Group:		Documentation

%description apidocs
Documentation for Python pexpect module.

%description apidocs -l pl.UTF-8
Dokumentacja do modułu Pythona pexpect.

%prep
%setup -q -n %{module}-%{version}
%patch -P 0 -p1

# fix invalid mapping
sed -i -e "s#^intersphinx_mapping =.*#intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}#g" doc/conf.py

%build
%py3_build

%if %{with tests}
# test_socket.py tests use network
# some test_replwrap.py tests have some expectation on bash PS1
LC_ALL=C.UTF-8 \
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
%{__python3} -m pytest tests -k 'not test_socket and not test_existing_spawn and not test_no_change_prompt and not test_pager_as_cat and not test_python'
%endif

%if %{with doc}
%{__make} -C doc html
%endif

%install
rm -rf $RPM_BUILD_ROOT

%py3_install

%{__rm} $RPM_BUILD_ROOT%{py3_sitescriptdir}/pexpect/bashrc.sh

install -d $RPM_BUILD_ROOT%{_examplesdir}/python3-%{module}-%{version}
cp -p examples/* $RPM_BUILD_ROOT%{_examplesdir}/python3-%{module}-%{version}
%{__sed} -i -e '1s,/usr/bin/env python,%{__python3},' $RPM_BUILD_ROOT%{_examplesdir}/python3-%{module}-%{version}/*.py
%{__sed} -i -e '1s,/usr/bin/python,%{__python3},' $RPM_BUILD_ROOT%{_examplesdir}/python3-%{module}-%{version}/cgishell.cgi
%{__sed} -i -e '2s,/usr/bin/env python,,' $RPM_BUILD_ROOT%{_examplesdir}/python3-%{module}-%{version}/cgishell.cgi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc LICENSE README.rst
%{py3_sitescriptdir}/pexpect
%{py3_sitescriptdir}/pexpect-%{version}-py*.egg-info
%{_examplesdir}/python3-%{module}-%{version}

%if %{with doc}
%files apidocs
%defattr(644,root,root,755)
%doc doc/_build/html/{_static,api,*.html,*.js}
%endif
