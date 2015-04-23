#!/usr/bin/env python

from setuptools import setup

setup(
    name='topicexplorer',
    version='1.0b2',
    description='InPhO Topic Explorer',
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
    packages=['topicexplorer', 'topicexplorer.lib', 'topicexplorer.extensions'],
    install_requires=[
        'bottle>=0.12', 
        'brewer2mpl>=1.4',
        'pystache>=0.5.4',
        'vsm==0.2',
        'wget',
        'unidecode',
        ],
    dependency_links=[
        'https://github.com/inpho/vsm/archive/master.zip#egg=vsm-0.2',
        ],
    scripts=['scripts/vsm', 'scripts/htutils']
)

