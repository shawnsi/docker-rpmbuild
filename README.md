docker-rpmbuild
===============

Builds RPMs inside a docker container.  A Dockerfile and build context are 
dynamically generated to construct the RPM development environment.  Then
`rpmbuild -ba` is executed and the RPM results are extracted.

Installation
------------

```bash
$ pip install git+https://github.com/shawnsi/docker-rpmbuild
```

Usage
-----

Build a simple spec file and source archive using rpmbuild in a docker image.

```bash
$ docker-rpmbuild --spec <path-to-spec> --source <path-to-source> <image>
```
