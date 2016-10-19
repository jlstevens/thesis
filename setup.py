#!/usr/bin/env python
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup_args = {}
setup_args.update(dict(
    name='stevens_thesis16',
    version="1.0",
    description='',
    long_description=open('README.rst').read() if os.path.isfile('README.rst') else 'Consult README.rst',
    author= "jlstevens",
    author_email= "jstevens@continuum.io",
    maintainer= "jlstevens",
    maintainer_email= "jlstevens@continuum.io",
    platforms=['Windows', 'Mac OS X', 'Linux'],
    packages = ["stevens_thesis16"],
    provides = ["stevens_thesis16"],
))


if __name__=="__main__":
    setup(**setup_args)
