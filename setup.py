#!/usr/bin/env python

from setuptools import setup

setup(
    name = 'docker-rpmbuild',
    version = '0.0.1',
    author = 'Shawn Siefkas',
    author_email = 'shawn.siefkas@meredith.com',
    description = 'Docker + rpmbuild = distributable',
    install_requires = [
        'docopt',
    ],
    entry_points = {
        'console_scripts': ['docker-rpmbuild = rpmbuild:main']
    },
    py_modules=['rpmbuild']
)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
