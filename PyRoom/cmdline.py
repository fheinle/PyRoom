#!/usr/bin/env python
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
PyRoom - A clone of WriteRoom
=============================

Based on code posted on ubuntu forums by NoWhereMan (www.nowhereland.it)
(Ubuntu thread was "WriteRoom/Darkroom/?")

:copyright: 2007 Nicolas P. Rougier & NoWhereMan Copyright
:copyright: 2008 The PyRoom Theme - See AUTHORS file for more information
:license: GNU General Public License, version 3 or later
"""

import gettext
from optparse import OptionParser
import sys
import os

import gtk

import PyRoom
from basic_edit import BasicEdit
from pyroom_error import handle_error
from preferences import PyroomConfig

__VERSION__ = PyRoom.__VERSION__

pyroom_config = PyroomConfig()

def main():
    sys.excepthook = handle_error

    files = []

    # Get commandline args
    parser = OptionParser(usage = _('%prog [-v] \
[file1] [file2]...'),
                        version = '%prog ' + __VERSION__,
                        description = _('PyRoom lets you edit text files \
simply and efficiently in a full-screen window, with no distractions.'))
    (options, args) = parser.parse_args()
    files = args

    # Create relevant buffers for file and load them
    pyroom = BasicEdit(pyroom_config=pyroom_config)
    buffnum = 0
    if len(files):
        for filename in files:
            pyroom.open_file_no_chooser(filename)
            buffnum += 1

    pyroom.set_buffer(buffnum)
    pyroom.status.set_text(
        _('Welcome to Pyroom %s, type Control-H for help') % __VERSION__
    )
    gtk.main()

if __name__ == '__main__':
    main()
