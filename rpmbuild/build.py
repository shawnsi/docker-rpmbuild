#!/usr/bin/env python

"""Docker rpmbuild.

Usage:
    docker-packager build [--define=<option>...]
                          (--source=<tarball>...|--sources-dir=<dir>)
                          (--spec=<file> [--retrieve] [--output=<path>]) 
                          <image>
    docker-packager rebuild --srpm=<file> [--output=<path>] <image>

Options:
    -h --help            Show this screen.
    --define=<option>    Pass a macro to rpmbuild.
    --output=<path>      Output directory for RPMs [default: .].
    --source=<tarball>   Tarball containing package sources.
    --sources-dir=<dir>  Directory containing resources required for spec.
    -r --retrieve        Fetch defined resources in spec file with spectool inside container
    --spec=<file>        RPM Spec file to build.
    --srpm=<file>        SRPM to rebuild.
"""

from __future__ import print_function

import json
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
            sources_dir=args['--sources-dir'],
            spec=args['--spec'],
            retrieve=args['--retrieve'],
        )

    if args['rebuild']:
        context = PackagerContext(
            args['<image>'],
            srpm=args['--srpm']
        )

    try:
        with Packager(context) as p:
            for line in p.build_image():
                parsed = json.loads(line.decode(encoding='UTF-8'))
                if 'stream' not in parsed:
                    print(parsed)
                print(parsed['stream'].strip())

            container, logs = p.build_package()

            for line in logs:
                print(line.decode(encoding='UTF-8').strip())

            for path in p.export_package(args['--output']):
                print('Wrote: %s' % path)

    except PackagerException:
        print('Container build failed!', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
