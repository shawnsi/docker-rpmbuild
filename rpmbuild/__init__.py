#!/usr/bin/env python

import os.path
import shutil
import tempfile
from subprocess import check_call

import docker

client = docker.Client()

class PackagerContext(object):
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

    def __init__(self, image, source, spec, output):
        self.image = image
        self.source = source
        self.spec = spec
        self.output = output

    def __str__(self):
        return self.path

    def setup(self):
        """
        Setup context for docker container build.  Copies the source tarball
        and SPEC file to the context directory.  Writes a Dockerfile from the
        template above.
        """
        self.path = tempfile.mkdtemp()
        self.dockerfile = os.path.join(self.path, 'Dockerfile')
        shutil.copy(self.source, self.path)
        shutil.copy(self.spec, self.path)
        with open(self.dockerfile, 'w') as f:
            content = self.template % (self.image, self.source, self.spec)
            f.write(content)

    def teardown(self):
        shutil.rmtree(self.path)


class PackagerException(Exception):
    pass

class Packager(object):

    def __init__(self, context):
        self.context = context

    def __enter__(self):
        self.context.setup()
        return self

    def __exit__(self, type, value, traceback):
        self.context.teardown()

    def __str__(self):
        return self.context.image

    def export_package(self, output):
        """
        Finds RPMs build in the container and copies to host output directory.
        """
        for diff in client.diff(self.container):
            if diff['Path'].startswith('/rpmbuild'):
                if diff['Path'].endswith('.rpm'):
                    resource = '%s:%s' % (self.container['Id'], diff['Path'])
                    # docker-py copy method is currently not working
                    check_call(['docker', 'cp', resource, output])

    def build(self):
        """
        Build the RPM package on top of the provided image.
        """
        logs = client.build(self.context.path, tag='rpmbuild-%s' % self.context.spec, stream=True)

        for line in logs:
            print line.strip()

        images = client.images(name='rpmbuild-%s' % self.context.spec)

        if not images:
            raise PackagerException

        image = images[0]

        self.container = client.create_container(image['Id'],
                'rpmbuild -ba %s' % os.path.join('/rpmbuild/SPECS', self.context.spec))
        client.start(self.container)
        client.wait(self.container)

        # Hack until https://github.com/dotcloud/docker-py/pull/105 is merged
        check_call(['docker', 'logs', self.container['Id']])

        self.export_package(self.context.output)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

