#!/usr/bin/env python

from setuptools import setup

setup(
    name='docker-rpmbuild',
    version='0.0.1',
    author='Shawn Siefkas',
    author_email='shawn.siefkas@meredith.com',
    description='Docker + rpmbuild=distributable',
    install_requires=[
        'docker-py==0.3.1',
        'docopt>=0.6.1',
        'Jinja2>=2.6',
    ],
    entry_points={
        'console_scripts': ['docker-rpmbuild=rpmbuild.build:main']
    },
    packages=['rpmbuild'],
)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
