#!/usr/bin/env python
# -*- coding:utf-8 -*-

# -----------------------------------------------------------------------------
# PyRoom - A clone of WriteRoom
# Copyright (c) 2007 Nicolas P. Rougier & NoWhereMan
# Copyright (c) 2008 The Pyroom Team - See AUTHORS file for more information
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

"""
global objects

Configuration, state keeping, etc
"""

import os
from sys import platform

if platform == 'win32':
    data_home, config_home = (os.environ['APPDATA'],) * 2
else:
    from xdg.BaseDirectory import xdg_config_home as config_home
    from xdg.BaseDirectory import xdg_data_home as data_home

# avoiding circular imports, actual import is below!
#from utils import FailsafeConfigParser

def get_gnome_fonts():
    """test if gnome font settings exist"""
    try:
        import gconf
    except ImportError:
        return
    gconf_client = gconf.Client()
    fonts = {'document':'', 'monospace':''}
    try:
        for font in fonts.keys():
            fonts[font] = gconf_client.get_value(
                '/desktop/gnome/interface/%s_font_name' % 
                font
            )
    except ValueError:
        return
    else:
        return fonts

state = dict(
    gnome_fonts = get_gnome_fonts(),
    absolute_path = os.path.dirname(os.path.abspath(__file__)),
    conf_dir = os.path.join(config_home, 'pyroom'),
    data_dir = os.path.join(data_home, 'pyroom'),
    themes_dir = os.path.join(data_home, 'pyroom', 'themes'),
    # XXX: works only in linux
    global_themes_dir = '/usr/share/pyroom/themes',
)

if not os.path.isdir(state['global_themes_dir']):
    if platform == 'win32':
        state['global_themes_dir'] = ''
    else: # run without installation
        state['global_themes_dir'] = os.path.join(
                state['absolute_path'],
                '..', 'themes')

# yes imports that are not quite obvious suck but we need to avoid
# circular imports here
from utils import FailsafeConfigParser            
config = FailsafeConfigParser()
config_file = os.path.join(state['conf_dir'], 'pyroom.conf')
if os.path.isfile(config_file):
    config.readfp(open(config_file, 'r'))
for d in [state['conf_dir'], state['themes_dir']]:
    if not os.path.isdir(d):
        os.makedirs(d)
