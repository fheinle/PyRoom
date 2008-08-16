#!/usr/bin/env python
# -*- coding:utf-8 -*-

from distutils.core import setup
import glob
import PyRoom

author = 'The Pyroom Team'
url = 'http://www.pyroom.org'

setup(
  name='PyRoom',
  version = PyRoom.__VERSION__,
  url = url,
  author = author,
  description = 'PyRoom is a distraction-free, fullscreen text editor',
  packages = ['PyRoom',],
  package_data = {'PyRoom':['interface.glade']},
  data_files = [
    ('/usr/share/pyroom/themes', glob.glob('themes/*.theme')),
    ('/usr/share/pyroom', ['pyroom.png']),
    ('/usr/share/applications', ['pyroom.desktop']),
  ],
  scripts=['pyroom',],
)
