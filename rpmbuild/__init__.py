#!/usr/bin/env python

import os
import shutil
import tempfile

from jinja2 import Template
import docker


class PackagerContext(object):
    # Hacking up the unintentional tarball unpack
    # https://github.com/dotcloud/docker/issues/3050
    template = Template("""
    FROM {{ image }}

    RUN yum -y install rpmdevtools yum-utils tar
    RUN rpmdev-setuptree

    {% if sources_dir is not none %}
    ADD SOURCES /rpmbuild/SOURCES
    {% endif %}
    {% for source in sources %}
    ADD {{ source }} /rpmbuild/SOURCES/{{ source }}
    RUN cd /rpmbuild/SOURCES; if [ -d {{ source }} ]; then mv {{ source }} {{ source }}.tmp; tar -C {{ source }}.tmp -czvf {{ source }} .; rm -r {{ source }}.tmp; fi
    RUN chown -R root:root /rpmbuild/SOURCES
    {% endfor %}

    {% if spec %}
    {% for macrofile in macrofiles %}
    ADD {{ macrofile }} /rpmbuild/SPECS/{{ macrofile }}
    {% endfor %}
    ADD {{ spec }} /rpmbuild/SPECS/{{ spec }}
    RUN chown -R root:root /rpmbuild/SPECS
    {% if retrieve %}
    RUN spectool -g -R -A /rpmbuild/SPECS/{{ spec }}
    {% endif %}
    RUN yum-builddep -y /rpmbuild/SPECS/{{ spec }}
    CMD rpmbuild {% for define in defines %} --define '{{ define }}' {% endfor %} -ba /rpmbuild/SPECS/{{ spec }}
    {% endif %}

    {% if srpm %}
    ADD {{ srpm }} /rpmbuild/SRPMS/{{ srpm }}
    RUN chown -R root:root /rpmbuild/SRPMS
    CMD rpmbuild --rebuild /rpmbuild/SRPMS/{{ srpm }}
    {% endif %}

    """)

    def __init__(self, image, defines=None, sources=None, sources_dir=None,
                 spec=None, macrofiles=None, retrieve=None, srpm=None):
        self.image = image
        self.defines = defines
        self.sources = sources
        self.macrofiles = macrofiles
        self.spec = spec
        self.srpm = srpm
        self.retrieve = retrieve

        if not defines:
            self.defines = []

        if not sources:
            self.sources = []

        if not macrofiles:
            self.macrofiles = []
 
        if sources_dir and os.path.exists(sources_dir):
            self.sources_dir = sources_dir
        else:
            self.sources_dir = None

        if image is None:
            raise PackagerException("Must provide base docker <image>")
 

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

        for macrofile in self.macrofiles:
            shutil.copy(macrofile, self.path)

        if self.spec:
            shutil.copy(self.spec, self.path)

        if self.srpm:
            shutil.copy(self.srpm, self.path)

        if self.sources_dir:
            shutil.copytree(self.sources_dir,
                            os.path.join(self.path, 'SOURCES'))
        
        with open(self.dockerfile, 'w') as f:
            content = self.template.render(
                image=self.image,
                defines=self.defines,
                sources=[os.path.basename(s) for s in self.sources],
                sources_dir=self.sources_dir,
                spec=self.spec and os.path.basename(self.spec),
                macrofiles=[os.path.basename(s) for s in self.macrofiles],
                retrieve=self.retrieve,
                srpm=self.srpm and os.path.basename(self.srpm),
            )
            f.write(content)

    def teardown(self):
        shutil.rmtree(self.path)


class PackagerException(Exception):
    pass


class Packager(object):

    def __init__(self, context, docker_config):
        self.context = context
        self.client = docker.Client(**dict(docker_config))

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

        for diff in self.client.diff(self.container):
            if diff['Path'].startswith('/rpmbuild'):
                if diff['Path'].endswith('.rpm'):
                    directory, name = os.path.split(diff['Path'])
                    res = self.client.copy(self.container['Id'], diff['Path'])
                    with open(os.path.join(output, name), 'wb') as f:
                        f.write(res.read()[512:])
                        exported.append(f.name)

        return exported

    @property
    def image_name(self):
        return 'rpmbuild-%s' % self.context

    @property
    def image(self):
        images = self.client.images(name=self.image_name)

        if not images:
            raise PackagerException

        return images[0]

    def build_image(self):
        return self.client.build(
            self.context.path,
            tag=self.image_name,
            stream=True
        )

    def build_package(self):
        """
        Build the RPM package on top of the provided image.
        """
        self.container = self.client.create_container(self.image['Id'])
        self.client.start(self.container)
        return self.container, self.client.logs(self.container, stream=True)


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
