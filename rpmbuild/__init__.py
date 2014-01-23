#!/usr/bin/env python

import os.path
import shutil
import tempfile

from jinja2 import Template
import docker

client = docker.Client()


class PackagerContext(object):
    template = Template("""
    FROM {{ image }}

    RUN yum -y install rpmdevtools yum-utils
    RUN rpmdev-setuptree

    {% for source in sources %}
    ADD {{ source }} /rpmbuild/SOURCES/{{ source }}
    RUN chown -R root:root /rpmbuild/SOURCES
    {% endfor %}

    {% if spec %}
    ADD {{ spec }} /rpmbuild/SPECS/{{ spec }}
    RUN chown -R root:root /rpmbuild/SPECS
    RUN yum-builddep -y /rpmbuild/SPECS/{{ spec }}
    CMD rpmbuild {% for define in defines %} --define '{{ define }}' {% endfor %} -ba /rpmbuild/SPECS/{{ spec }}
    {% endif %}

    {% if srpm %}
    ADD {{ srpm }} /rpmbuild/SRPMS/{{ srpm }}
    RUN chown -R root:root /rpmbuild/SRPMS
    CMD rpmbuild --rebuild /rpmbuild/SRPMS/{{ srpm }}
    {% endif %}

    """)

    def __init__(self, image, defines=None, sources=None, spec=None, srpm=None):
        self.image = image
        self.defines = defines
        self.sources = sources
        self.spec = spec
        self.srpm = srpm

        if not defines:
            self.defines = []

        if not sources:
            self.sources = []

    def __str__(self):
        return self.spec or self.srpm

    def setup(self):
        """
        Setup context for docker container build.  Copies the source tarball
        and SPEC file to the context directory.  Writes a Dockerfile from the
        template above.
        """
        self.path = tempfile.mkdtemp()
        self.dockerfile = os.path.join(self.path, 'Dockerfile')

        for source in self.sources:
            shutil.copy(source, self.path)

        if self.spec:
            shutil.copy(self.spec, self.path)

        if self.srpm:
            shutil.copy(self.srpm, self.path)

        with open(self.dockerfile, 'w') as f:
            content = self.template.render(
                image=self.image,
                defines=self.defines,
                sources=[os.path.basename(s) for s in self.sources],
                spec=self.spec and os.path.basename(self.spec),
                srpm=self.srpm and os.path.basename(self.srpm),
            )
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
        exported = []

        for diff in client.diff(self.container):
            if diff['Path'].startswith('/rpmbuild'):
                if diff['Path'].endswith('.rpm'):
                    directory, name = os.path.split(diff['Path'])
                    res = client.copy(self.container['Id'], diff['Path'])
                    with open(os.path.join(output, name), 'w') as f:
                        f.write(res.read()[512:])
                        exported.append(f.name)

        return exported

    @property
    def image_name(self):
        return 'rpmbuild-%s' % self.context

    @property
    def image(self):
        images = client.images(name=self.image_name)

        if not images:
            raise PackagerException

        return images[0]

    def build_image(self):
        return client.build(
            self.context.path,
            tag=self.image_name,
            stream=True
        )

    def build_package(self):
        """
        Build the RPM package on top of the provided image.
        """
        self.container = client.create_container(self.image['Id'])
        client.start(self.container)
        return self.container, client.logs(self.container, stream=True)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
