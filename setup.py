#!/usr/bin/env python

from setuptools import setup

setup(
    name='docker-rpmbuild',
    version='0.0.1',
    author='Shawn Siefkas',
    author_email='shawn.siefkas@meredith.com',
    description='Docker + rpmbuild=distributable',
    install_requires=[
        'docker-py>=0.2.3',
        'docopt==0.6.1',
    ],
    entry_points={
        'console_scripts': ['docker-rpmbuild=rpmbuild.build:main']
    },
    packages=['rpmbuild'],
)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
