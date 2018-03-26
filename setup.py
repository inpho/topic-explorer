#!/usr/bin/env python

from setuptools import setup
import os
import os.path

# get version from package through manual read
# see http://stackoverflow.com/a/17626524
__version__ = open(os.path.normpath("topicexplorer/version.py")).readlines()[11].split()[-1].strip("\"'")
os.environ['PBR_VERSION'] = __version__

# PyPandoc
if os.path.exists('README.txt'):
    long_description = open('README.txt').read()
else:
    long_description = ''

setup(
    pbr=True,
    setup_requires=['pbr'],
    version=__version__,
    long_description = long_description,
    test_suite="unittest2.collector",
    tests_require=['unittest2']
)

