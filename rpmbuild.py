#!/usr/bin/env python

"""Docker rpmbuild.

Usage:
    docker-packager build [--source=<path>] <spec>

Options:
    -h --help           Show this screen.
    --source=<path>     Path to the directory containg a Dockerfile [default: .].

"""

import os.path
import sys
from subprocess import check_call

from docopt import docopt
import docker

client = docker.Client()

class PackagerException(Exception):
    pass

class Packager(object):

    def __init__(self, source):
        self.source = source

    def __enter__(self):
        self.image, logs = client.build(self.source)
        print logs

        if not self.image:
            raise PackagerException

        return self

    def __exit__(self, type, value, traceback):
        pass

    def __str__(self):
        return self.image

    def build(self, spec):
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

