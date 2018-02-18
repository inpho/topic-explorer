#!/usr/bin/env python

from distutils.command.install_data import install_data as _install_data
from setuptools import setup, find_packages
import os
import platform
import os.path

# get version from package through manual read
# see http://stackoverflow.com/a/17626524
__version__ = open(os.path.normpath("topicexplorer/version.py")).readlines()[11].split()[-1].strip("\"'")

# Specializations of some distutils command classes
# first install data files to actual library directory
class PostInstallData(_install_data):
    """need to change self.install_dir to the actual library dir"""
    def run(self):
        import nltk
        runcmd = _install.run(self)
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        return runcmd

# PyPandoc
if os.path.exists('README.txt'):
    long_description = open('README.txt').read()
else:
    long_description = ''

setup(
    pbr=True,
    setup_requires=['pbr', 'nltk'],
    version=__version__,
    long_description = long_description,
    cmdclass={'install_data' : PostInstallData},
    test_suite="unittest2.collector",
    tests_require=['unittest2', 'mock']
)

