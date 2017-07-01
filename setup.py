#!/usr/bin/env python
from distutils.command.install_data import install_data as _install_data
from distutils.command.install import install as _install
from setuptools import setup, find_packages
import os
import platform
try:
    # Python 3 or Python 2 w/backport
    from importlib import reload
except ImportError:
    # Python 2 without backports, use default reload
    pass

# get version from package through manual read
# see http://stackoverflow.com/a/17626524 
__version__ = open("topicexplorer/version.py").readlines()[9].split()[-1].strip("\"'")

# building datafiles list
datadir = 'www'
def get_datafiles(datadir):
    return [(root, [os.path.join(root, f) for f in files])
                for root, dirs, files in os.walk(datadir)]

datafiles = get_datafiles('www')
datafiles.extend(get_datafiles('demo'))
datafiles.extend(get_datafiles('ipynb'))

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

setup_requires = [ 'nltk' ]

install_requires = [
        'bottle>=0.12', 
        'brewer2mpl>=1.4',
        'pystache>=0.5.4',
        'vsm>=0.4.0rc1',
        'wget',
        'unidecode',
        'pyenchant==1.6.6',
        'networkx>=1.9.1',
        'matplotlib>=1.5.0',
        'pip>=7.1.1',
        'langdetect',
        'profilehooks',
        'pybtex>=0.20',
        'paste',
        'htrc-feature-reader>=1.90'
        ]

if platform.system() == 'Windows':
    install_requires.append('pywin32')
#else:
#    install_requires.append('mmseg==1.3.0')

if platform.python_version_tuple()[0] == '2':
    install_requires.append("futures>=3.0.0")
    install_requires.append("configparser>=3.5.0")
    install_requires.append("pdfminer")
    install_requires.append("importlib")
elif platform.python_version_tuple()[0] == '3':
    install_requires.append("pdfminer3k")

setup(
    name='topicexplorer',
    version=__version__,
    description='InPhO Topic Explorer',
    long_description = long_description,
    author = "The Indiana Philosophy Ontology (InPhO) Project",
    author_email = "inpho@indiana.edu",
    url='http://inphodata.cogs.indiana.edu',
    download_url='http://github.com/inpho/topic-explorer',
    keywords = [],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Bottle",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Text Processing :: Linguistic",
        ],
    packages=find_packages(),
    data_files=datafiles,
    setup_requires=setup_requires,
    install_requires=install_requires,
    dependency_links=[
        'https://github.com/inpho/vsm/archive/py3k.zip#egg=vsm-dev',
        'https://inpho.cogs.indiana.edu/pypi/pymmseg/'
        ],
    include_package_data=True,
    zip_safe=False,
    cmdclass = { 'install_data': PostInstallData },
    entry_points={
        'console_scripts' : ['vsm = topicexplorer.__main__:vsm',
                'topicexplorer = topicexplorer.__main__:main',
                'htutils = topicexplorer.lib.hathitrust:main']
    }
)

