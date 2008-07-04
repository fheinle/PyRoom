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

"""

import gtk, pango
import traceback

class PyroomError(Exception):
    """our nice little exception"""
    pass

def handle_error(exception_type, exception_value, exception_traceback):
    """display errors to the end user using dialog boxes"""
    if exception_type == PyroomError:
        message = exception_value.message
    else: # uncaught exception in code
        message = _("""There has been an uncaught exception in pyroom.
This is most likely a programming error. Please submit a bug report
to launchpad""")

    error_dialog = gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL,
                type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_NONE,
                message_format=message)
    error_dialog.set_title('Fehler')
    error_dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
    error_dialog.add_button (_("Details..."), 2)
    error_dialog.set_position(gtk.WIN_POS_CENTER)
    error_dialog.set_gravity(gtk.gdk.GRAVITY_CENTER)
    error_dialog.show_all()
    resp = error_dialog.run()
    if resp == 2:
        details_dialog = gtk.Dialog(_('Bug details'), error_dialog, 
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
		    (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
        )
        textview = gtk.TextView()
        textview.show()
        textview.set_editable (False)
        textview.modify_font(pango.FontDescription ("Monospace"))
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.show()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(textview)
        details_dialog.vbox.add(scrolled_window)
        textbuffer = textview.get_buffer()
        printable_traceback = "\n".join(
            traceback.format_exception(
                exception_type, 
                exception_value,
                exception_traceback
            )
        )
        textbuffer.set_text(printable_traceback)
        monitor = gtk.gdk.screen_get_default().\
                  get_monitor_at_window(error_dialog.window)
        area = gtk.gdk.screen_get_default().get_monitor_geometry(monitor)
        details_width = area.width // 1.6
        details_height = area.height // 1.6
        details_dialog.set_default_size(int(details_width), int(details_height))
        details_dialog.run()
        details_dialog.destroy()
    error_dialog.destroy()
