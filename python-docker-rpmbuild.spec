Name:           python-docker-rpmbuild
Version:        0.0.1
Release:        1%{?dist}
Summary:        Docker + rpmbuild = distributable

License:        MIT
Source0:        python-docker-rpmbuild-%{version}.tar.gz

Requires:       python-docopt
BuildRequires:  python-setuptools
BuildArch:      noarch

%description
Docker wrapper for rpmbuild.

%prep
%setup -q -c -n python-docker-rpmbuild-%{version}

%build
%{__python} setup.py build

%install
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT

%files
/usr/bin/docker-rpmbuild
%{python_sitelib}/rpmbuild*
%{python_sitelib}/docker_rpmbuild-*.egg-info

%changelog
* Tue Dec 10 2013 Shawn Siefkas <shawn.siefkas@meredith.com> - 0.0.1-1
- Initial Spec File
