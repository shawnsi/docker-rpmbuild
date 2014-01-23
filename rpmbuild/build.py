#!/usr/bin/env python

"""Docker rpmbuild.

Usage:
    docker-packager build [--define=<option>...] --spec=<file> --source=<tarball>...
        [--output=<path>] <image>
    docker-packager rebuild --srpm=<file> [--output=<path>] <image>

Options:
    -h --help           Show this screen.
    --define=<option>   Pass a macro to rpmbuild.
    --output=<path>     Output directory for RPMs [default: .].
    --source=<tarball>  Tarball containing package sources.
    --spec=<file>       RPM Spec file to build.
    --srpm=<file>       SRPM to rebuild.

"""

import sys

from docopt import docopt
from rpmbuild import Packager, PackagerContext, PackagerException


def main():
    args = docopt(__doc__, version='Docker Packager 0.0.1')

    if args['build']:
        context = PackagerContext(
            args['<image>'],
            defines=args['--define'],
            sources=args['--source'],
            spec=args['--spec'],
        )

    if args['rebuild']:
        context = PackagerContext(
            args['<image>'],
            srpm=args['--srpm']
        )

    try:
        with Packager(context) as p:
            for line in p.build_image():
                print line.strip()

            container, logs = p.build_package()

            for line in logs:
                print line.strip()

            for path in p.export_package(args['--output']):
                print 'Wrote: %s' % path

    except PackagerException:
        print >> sys.stderr, 'Container build failed!'
        sys.exit(1)

if __name__ == '__main__':
    main()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
