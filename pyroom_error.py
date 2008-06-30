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
Errors raised within pyroom

TODO: make this somehow useful
"""

import gtk

class PyroomError(Exception):
    """our nice little exception"""
    pass

def handle_error(exception_type, exception_value, traceback):
    """display errors to the end user using dialog boxes"""
    dialog = gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL,
                type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_NONE,
                message_format=exception_value.message)
    dialog.set_title('Fehler')
    dialog.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
    dialog.set_position(gtk.WIN_POS_CENTER)
    dialog.set_gravity(gtk.gdk.GRAVITY_CENTER)
    dialog.show_all()
    dialog.run()
    dialog.destroy()
