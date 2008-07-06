#!/usr/bin/env python
# -*- coding:utf-8 -*-

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

import PyRoom

author = 'The Pyroom Team'
url = 'http://www.pygments.org'

setup(
    name = 'PyRoom',
    version = PyRoom.__VERSION__,
    url = url,
    author = author,
    description = 'PyRoom is a distraction-free, fullscreen text editor',
    keywords = 'text editor',
    packages = find_packages(),
    entry_points = {
        'console_scripts': ['pyroom = PyRoom.cmdline:main',]
    },
    platforms = 'any',
    include_package_data = True,
    classifiers = [
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Intended Audience :: End Users/Desktop',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ],
)
