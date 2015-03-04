#!/usr/bin/env python

"""Docker rpmbuild.

Usage:
    docker-rpmbuild build [--config=<file>]
                          [--docker-base_url=<url>]
                          [--docker-timeout=<seconds>]
                          [--docker-version=<version>]
                          [--define=<option>...]
                          (--source=<tarball>...|--sources-dir=<dir>)
                          (--spec=<file> [--macrofile=<file>...] [--retrieve] [--output=<path>])
                          <image>
    docker-rpmbuild rebuild [--config=<file>]
                            [--docker-base_url=<url>]
                            [--docker-timeout=<seconds>]
                            [--docker-version=<version>]
                            (--srpm=<file> [--output=<path>])
                            <image>

Options:
    -h --help            Show this screen.
    --config=<file>      Configuration file [default: /etc/docker-packager/rpmbuild.ini]
    --define=<option>    Pass a macro to rpmbuild.
    --output=<path>      Output directory for RPMs [default: .].
    --source=<tarball>   Tarball containing package sources.
    --sources-dir=<dir>  Directory containing resources required for spec.
    -r --retrieve        Fetch defined resources in spec file with spectool inside container
    --spec=<file>        RPM Spec file to build.
    --macrofile=<file>   Defines added in a file, will reside together with SPECS/
    --srpm=<file>        SRPM to rebuild.

Docker Options:
    --docker-base_url=<url>     protocol+hostname+port towards docker
                                (example: unix://var/run/docker.sock)
    --docker-timeout=<seconds>  HTTP request timeout in seconds towards docker API. (default: 600)
    --docker-version=<version>  API version the docker client will use towards
                                docker (example: 1.12)
"""

from __future__ import print_function

import json
import sys

from docopt import docopt
from rpmbuild import Packager, PackagerContext, PackagerException
from rpmbuild.config import get_docker_config


def main():
    args = docopt(__doc__, version='Docker Packager 0.0.1')

    if args['build']:
        context = PackagerContext(
            args['<image>'],
            defines=args['--define'],
            sources=args['--source'],
            sources_dir=args['--sources-dir'],
            spec=args['--spec'],
            macrofiles=args['--macrofile'],
            retrieve=args['--retrieve'],
        )

    if args['rebuild']:
        context = PackagerContext(
            args['<image>'],
            srpm=args['--srpm']
        )

    try:
        with Packager(context,  get_docker_config(args)) as p:
            for line in p.build_image():
                parsed = json.loads(line.decode(encoding='UTF-8'))
                if 'stream' not in parsed:
                    print(parsed)
                else:
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
