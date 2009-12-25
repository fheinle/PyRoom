# -*- coding: utf-8 -*-
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
helper functions
"""

import os
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError
# avoiding circular imports, actual import is below!
# from globals import state

DEFAULT_CONF = {
    'visual':{
        'theme':'green',
        'showborder':'1',
        'showpath':'1',
        'linespacing':'2',
        'custom_font':'Sans 12',
        'use_font_type':'custom',
        'indent':0,
        'alignment':'center',
    },
    'editor':{
        'session':'True',
        'autosavetime':'2',
        'autosave':'0',
    },
}

class FailsafeConfigParser(SafeConfigParser):
    """
    Config parser that returns default values 

    Two reasons for implementation: we don't want pyroom to break while
    running on legacy configuration files. Second reason: standard 
    'defaults' behaviour of ConfigParser is stupid, doesn't allow for 
    sections and works with a lot of magic. 
    """
    def get(self, section, option):
        """
        return default values instead of breaking

        this is a drop-in replacement for standard get from ConfigParser
        """
        try:
            return SafeConfigParser.get(self, section, option)
        except NoOptionError:
            try:
                default_value = DEFAULT_CONF[section][option]
            except KeyError:
                raise NoOptionError(option, section)
            else:
                return default_value
        except NoSectionError:
            self.add_section(section)
            return self.get(section, option)

# yes imports that are not quite obvious suck but we need to avoid
# circular imports here
from globals import state

def build_default_conf():
    """builds necessary default conf.

    * makes directories if not here,
    * copies theme data
    * builds the default conf file
    """
    new_config = FailsafeConfigParser()
    if not os.path.isdir(state['conf_dir']):
        os.makedirs(state['conf_dir'])
        for section, settings in DEFAULT_CONF.items():
            new_config.add_section(section)
            for key, value in settings.items():
                new_config.set(section, key, str(value))
        config_file = open(
            os.path.join(state['conf_dir'], 'pyroom.conf'
        ), 'w')
        new_config.write(config_file)
        config_file.close()
    if not os.path.isdir(state['themes_dir']):
        os.makedirs(state['themes_dir'])

def get_themes_list():
    """get all the theme files sans file suffix and the custom theme"""
    themeslist = []
    rawthemeslist = os.listdir(state['themes_dir'])
    globalthemeslist = os.listdir(state['global_themes_dir'])
    for themefile in rawthemeslist:
        if themefile.endswith('theme') and themefile != 'custom.theme':
            themeslist.append(themefile[:-6])
    for themefile in globalthemeslist:
        if themefile.endswith('theme') and themefile != 'custom.theme':
            # TODO : do not add in the themelist a theme already existing in
            # the personal directory
            if not themefile[:-6] in themeslist:
                themeslist.append(themefile[:-6])
    return themeslist


