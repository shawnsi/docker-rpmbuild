#!/usr/bin/env python

"""Docker rpmbuild.

Usage:
    docker-packager --spec=<file> --source=<tarball> [--output=<path>] <image>

Options:
    -h --help           Show this screen.
    --output=<path>     Output directory for RPMs [default: .].
    --source=<tarball>  Tarball containing package sources.
    --spec=<file>       RPM Spec file to build.

"""

import os.path
import shutil
import sys
import tempfile
from subprocess import check_call

from docopt import docopt
import docker

client = docker.Client()

template = """
FROM %s

ENV SOURCE %s
ENV SPEC %s

RUN yum -y install rpmdevtools yum-utils
RUN rpmdev-setuptree

ADD $SOURCE /rpmbuild/SOURCES/$SOURCE
Run chown root:root /rpmbuild/SOURCES/$SOURCE
ADD $SPEC /rpmbuild/SPECS/$SPEC
RUN chown root:root /rpmbuild/SPECS/$SPEC
RUN yum-builddep -y /rpmbuild/SPECS/$SPEC
"""

class PackagerException(Exception):
    pass

class Packager(object):

    def __init__(self, image):
        self.image = image

    def __enter__(self):
        self.context = tempfile.mkdtemp()
        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.context)

    def __str__(self):
        return self.image

    def export_package(self, output):
        for diff in client.diff(self.container):
            if diff['Path'].startswith('/rpmbuild'):
                if diff['Path'].endswith('.rpm'):
                    resource = '%s:%s' % (self.container['Id'], diff['Path'])
                    check_call(['docker', 'cp', resource, output])

    def prepare_context(self, source, spec):
        shutil.copy(source, self.context)
        shutil.copy(spec, self.context)
        dockerfile = template % (self.image, source, spec)
        with open(os.path.join(self.context, 'Dockerfile'), 'w') as f:
            f.write(dockerfile)

    def build(self, source, spec, output):
        self.prepare_context(source, spec)
        self.image, logs = client.build(self.context)
        print logs

        if not self.image:
            raise PackagerException

        self.container = client.create_container(self.image,
                'rpmbuild -ba %s' % os.path.join('/rpmbuild/SPECS', spec))
        client.start(self.container)
        client.wait(self.container)

        # Hack until https://github.com/dotcloud/docker-py/pull/105 is merged
        check_call(['docker', 'logs', self.container['Id']])

        self.export_package(output)


def main():
    args = docopt(__doc__, version='Docker Packager 0.0.1')

    try:
        with Packager(args['<image>']) as p:
            p.build(args['--source'], args['--spec'], args['--output'])

    except PackagerException:
        print >> sys.stderr, 'Container build failed!'
        sys.exit(1)

if __name__ == '__main__':
    main()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

