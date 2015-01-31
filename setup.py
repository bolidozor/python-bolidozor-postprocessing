#!/usr/bin/python
# -*- coding: utf8 -*-

from setuptools import setup, find_packages
import sys
import os
import os.path as path


os.chdir(path.realpath(path.dirname(__file__)))
sys.path.insert(1, 'src')
import bzpost


setup(
    name             = 'bzpost',
    version          = bzpost.__version__,
    author           = 'Jan Milík',
    author_email     = 'milikjan@fit.cvut.cz',
    description      = 'Bolidozor postprocessing functions.',
    long_description = bzpost.__doc__,
    #url              = 'https://github.com/MLAB-project/python-mlab-utils',

    #packages    = ['pymlab', 'pymlab.sensors', 'pymlab.tests', ],
    packages    = find_packages("src"),
    package_dir = {'': 'src'},
    provides    = ['bzpost'],
    install_requires = [ ],
    keywords = ['Bolidozor', 'library', ],
    license     = 'Lesser General Public License v3',
    #download_url = 'https://github.com/MLAB-project/python-mlab-utils/archive/0.1.tar.gz',
    
    test_suite = 'tests',

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: Czech',
        # 'Operating System :: OS Independent',
        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)

