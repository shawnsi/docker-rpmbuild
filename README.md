docker-rpmbuild
===============

**This project has not been maintained for some time and does not work with recent docker version.  Please see https://github.com/alanfranz/docker-rpm-builder instead.**

[![Build Status](https://travis-ci.org/shawnsi/docker-rpmbuild.png)](https://travis-ci.org/shawnsi/docker-rpmbuild)

Builds RPMs inside a docker container.  A Dockerfile and build context are 
dynamically generated to construct the RPM development environment.  Then
`rpmbuild -ba` is executed and the RPM results are extracted.

Installation
------------

```bash
$ pip install git+https://github.com/shawnsi/docker-rpmbuild
```

Build from SPEC
---------------

Build a simple spec file and source archive using rpmbuild in a docker image.

```bash
$ docker-rpmbuild build --spec <path-to-spec> --source <path-to-source> <image>
```

Build from SRPM
---------------

Rebuild an existing SRPM package.

```bash
$ docker-rpmbuild rebuild --srpm <path-to-srpm> <image>
```
