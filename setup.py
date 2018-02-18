#!/usr/bin/env python

from distutils.command.install_data import install_data as _install_data
from distutils.command.install import install as _install
from setuptools import setup, find_packages
import os
import platform
import os.path

try:
    # Python 3 or Python 2 w/backport
    from importlib import reload
except ImportError:
    # Python 2 without backports, use default reload
    pass

# get version from package through manual read
# see http://stackoverflow.com/a/17626524
__version__ = open(os.path.normpath("topicexplorer/version.py")).readlines()[11].split()[-1].strip("\"'")

# Specializations of some distutils command classes
# first install data files to actual library directory
class PostInstallData(_install_data):
    """need to change self.install_dir to the actual library dir"""
    def run(self):
        import nltk
        runcmd = _install_data.run(self)
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        return runcmd

# PyPandoc
import os
if os.path.exists('README.txt'):
    long_description = open('README.txt').read()
else:
    long_description = ''

#else:
#    install_requires.append('mmseg==1.3.0')

setup(
    pbr=True,
    setup_requires=['pbr'],
    version=__version__,
    long_description = long_description,
    dependency_links=[
        'https://inpho.cogs.indiana.edu/pypi/pymmseg/'
        ],
    test_suite="unittest2.collector",
    tests_require=['unittest2', 'mock']
)

