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

import traceback
import sys
import os.path
import gobject
import gtk
import gettext
import getopt
gettext.install('pyroom', 'locale')

from basic_edit import BasicEdit
# Some styles

from styles import styles
if __name__ == '__main__':
    style = 'green'
    verbose = True
    ret = False
    files = []


    # Get commandline args
    try:
        args, files = getopt.getopt(sys.argv[1:],'vs', ['style='])
    except getopt.GetoptError:
    # Print help information
        print _("Usage: pyroom [-v] [-s] [--style={style name}] file1 file2")
        sys.exit(2)
    style_true = False
    for arg, val in args:
        if arg == '-v':
            verbose = True
        elif arg == '--style':
            if val in styles:
                style = val
        elif arg == '-s':
            ret = True

    # Create relevant buffers for file and load them
    pyroom = BasicEdit(styles[style],verbose, ret)
    if len(files):
        for filename in files:
            buffer = pyroom.new_buffer()
            buffer.filename = filename
            if os.path.exists(filename):
                try:
                    print "Automatically opened %s" %(filename)
                    f = open(filename, 'r')
                    buffer.begin_not_undoable_action()
                    buffer.set_text(unicode(f.read(), 'utf-8'))
                    buffer.end_not_undoable_action()
                    f.close()
                except IOError, (errno, strerror):
                    errortext = '''Unable to open %(filename)s.''' % {'filename': buffer.filename}
                    if errno == 13:
                        errortext += _(' You do not have permission to open the file.')
                    buffer.set_text(_(errortext))
                    if verbose:
                        print (_('Unable to open %(filename)s. %(traceback)s'
                                 % {'filename': buffer.filename,
                                 'traceback': traceback.format_exc()})
                        )
                    buffer.filename = FILE_UNNAMED
                except:
                    buffer.set_text(_('Unable to open %s\n'
                                     % buffer.filename))
                    if verbose:
                        print (_('Unable to open %(filename)s. %(traceback)s'
                                % {'filename': buffer.filename,
                                'traceback': traceback.format_exc()}))
                    buffer.filename = FILE_UNNAMED

        pyroom.set_buffer(0)
        pyroom.close_buffer()

    gtk.main()

# EOF
