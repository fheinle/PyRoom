#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
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
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------------------------
#
# Based on code posted on ubuntu forums by NoWhereMan (www.nowhereland.it)
#  (Ubuntu thread was "WriteRoom/Darkroom/?")
#
# ------------------------------------------------------------------------------

import sys
import os.path
import gobject
import gtk
import gettext
import getopt
import traceback
gettext.install('pyroom', 'locale')
import ConfigParser
from basic_edit import BasicEdit
import autosave
from pyroom_error import PyroomError
# Some styles

if __name__ == '__main__':

    verbose = False

    files = []
    config = ConfigParser.ConfigParser()
    config.read("example.conf")
    style = config.get("visual","theme")
    autosave.autosave_time=config.get("editor","autosavetime")
    # Get commandline args
    try:
        args, files = getopt.getopt(sys.argv[1:],'vC', ['style=','autosave_time='])
    except getopt.GetoptError:
    # Print help information
        print _("Usage: pyroom [-v] [--style={style name}] file1 file2")
        sys.exit(2)
    style_true = False
    for arg, val in args:
        if arg == '-v':
            verbose = True
        elif arg == '--style':
                style = val
        elif arg == '--autosave_time':
            autosave.autosave_time=int(val) #set autosave timeout on user request

    # Create relevant buffers for file and load them
    pyroom = BasicEdit(style,verbose)
    try:
        buffnum = 0
        if len(files):
            for filename in files:
                pyroom.open_file_no_chooser(filename)
                buffnum += 1

        pyroom.set_buffer(buffnum)
        pyroom.status.set_text(
            _('Welcome to PyRoom 0.2b, type Control-H for help'))
        gtk.main()
    except PyroomError, e:
        # To change the format of the error text, edit pyroom_error
        pyroom.gui.error.set_text(str(e))
        if verbose:
            print str(e)
            print e.traceback
    except:
        print traceback.format_exc()


# EOF
