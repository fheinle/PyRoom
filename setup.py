#!/usr/bin/env python
# -*- coding:utf-8 -*-

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

import PyRoom
import os

author = 'The Pyroom Team'
url = 'http://www.pyroom.org'

def gather_files(files_dir):
    """gather filenames for easy integration of locales"""
    files = []
    for directory in os.walk(files_dir):
        for filename in directory[2]:
            included_file = os.path.join(
                directory[0],
                filename
            ).lstrip(files_dir + '/')
            files.append(included_file)
    return files

install_requires = []

print "Checking for PyGTK"
try: # quite hackish workaround for distros with pygtk packages
    import gtk
except ImportError:
    print "PyGTK not found, will try to install"
    install_requires.append('PyGTK')
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
    package_data = {
        'PyRoom':['interface.glade'],
        'themes':['*.theme'],
        'locales':gather_files('locales'),
    },
    install_requires = install_requires,
)
