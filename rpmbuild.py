#!/usr/bin/env python

"""Docker rpmbuild.

Usage:
    docker-packager build [--source=<path>] <spec>

Options:
    -h --help           Show this screen.
    --source=<path>     Path to the directory containg a Dockerfile [default: .].

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
FROM centos

RUN yum -y localinstall http://mirror.rit.edu/epel/6/x86_64/epel-release-6-8.noarch.rpm
RUN yum -y install rpmdevtools yum-utils
RUN rpmdev-setuptree

ADD %s.spec /rpmbuild/SPECS/
RUN chown root:root /rpmbuild/SPECS/%s.spec
RUN yum-builddep -y /rpmbuild/SPECS/%s.spec
ADD . /tmp/sources
RUN chown -R root:root /tmp/sources
RUN tar -C /tmp/sources -czvf /rpmbuild/SOURCES/%s-0.0.1.tar.gz --exclude .git .
"""

class PackagerException(Exception):
    pass

class Packager(object):

    def __init__(self, source):
        self.source = source
        self.temp = tempfile.mkdtemp()
        self.context = os.path.join(self.temp, 'context')

    def __enter__(self):
        shutil.copytree(self.source, self.context)
        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.temp)

    def __str__(self):
        return self.image

    def create_dockerfile(self, spec):
        name, extension = os.path.splitext(spec)
        dockerfile = template % (name, name, name, name)
        with open(os.path.join(self.context, 'Dockerfile'), 'w') as f:
            f.write(dockerfile)

    def build(self, spec):
        self.create_dockerfile(spec)
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
    

def main():
    args = docopt(__doc__, version='Docker Packager 0.0.1')

    if args['build']:
        try:
            with Packager(args['--source']) as p:
                p.build(args['<spec>'])

        except PackagerException:
            print >> sys.stderr, 'Container build failed!'
            sys.exit(1)

if __name__ == '__main__':
    main()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

