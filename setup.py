#!/usr/bin/env python
from distutils.command.install_data import install_data as _install_data
from distutils.command.install import install as _install
from setuptools import setup, find_packages
import os
import platform

# building datafiles list
datadir = 'www'
def get_datafiles(datadir):
    return [(root, [os.path.join(root, f) for f in files])
                for root, dirs, files in os.walk(datadir)]

datafiles = get_datafiles('www')
datafiles.extend(get_datafiles('ipynb'))

# After install, download nltk packages 'punkt' and 'stopwords'
# http://blog.diffbrent.com/correctly-adding-nltk-to-your-python-package-using-setup-py-post-install-commands/
def _post_install(dir):
    import site
    reload(site)

    import nltk
    nltk.download('punkt')
    nltk.download('stopwords')

# Specializations of some distutils command classes
# first install data files to actual library directory
class wx_smart_install_data(_install_data):
    """need to change self.install_dir to the actual library dir"""
    def run(self):
        install_cmd = self.get_finalized_command('install')
        self.install_dir = getattr(install_cmd, 'install_lib')
        self.execute(_post_install, (self.install_dir,),
                     msg="Running post install task")
        return _install_data.run(self)

# PyPandoc
import os
if os.path.exists('README.txt'):
    long_description = open('README.txt').read()
else:
    long_description = '' 

install_requires = [
        'bottle>=0.12', 
        'brewer2mpl>=1.4',
        'pystache>=0.5.4',
        'vsm>=0.3.3',
        'wget',
        'unidecode',
        'pdfminer',
        'pyenchant'
        ]

if platform.system() == 'Windows':
    install_requires.append('pywin32')

setup(
    name='topicexplorer',
    version='1.0b24',
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
    install_requires=install_requires,
    dependency_links=[
        'https://github.com/inpho/vsm/archive/master.zip#egg=vsm-0.3.3',
        ],
    include_package_data=True,
    cmdclass = { 'install_data': wx_smart_install_data },
    entry_points={
        'console_scripts' : ['vsm = topicexplorer.__main__:main',
                'htutils = topicexplorer.lib.hathitrust:main']
    }
)

