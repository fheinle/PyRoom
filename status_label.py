# status_label.py - status bar
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

"""status_label.py - status bar

provides a fading status bar that displays information to the user

"""


import gobject
import gtk


class FadeLabel(gtk.Label):
    """ GTK Label with timed fade out effect """

    active_duration = 3000  # Fade start after this time
    fade_duration = 1500.0  # Fade duration

    def __init__(self, message='', active_color=None, inactive_color=None):
        gtk.Label.__init__(self, message)
        if not active_color:
            active_color = '#ffffff'
        self.active_color = active_color
        if not inactive_color:
            inactive_color = '#000000'
        self.fade_level = 0
        self.inactive_color = inactive_color
        self.idle = 0

    def set_text(self, message, duration=None):
        """change text that is displayed
        @param message: message to display
        @param duration: duration in miliseconds"""
        if not duration:
            duration = self.active_duration
        self.modify_fg(gtk.STATE_NORMAL,
                       gtk.gdk.color_parse(self.active_color))
        gtk.Label.set_text(self, message)
        if self.idle:
            gobject.source_remove(self.idle)
        self.idle = gobject.timeout_add(duration, self.fade_start)

    def fade_start(self):
        """start fading timer"""
        self.fade_level = 1.0
        if self.idle:
            gobject.source_remove(self.idle)
        self.idle = gobject.timeout_add(25, self.fade_out)

    def fade_out(self):
        """now fade out"""
        color = gtk.gdk.color_parse(self.inactive_color)
        (red1, green1, blue1) = (color.red, color.green, color.blue)
        color = gtk.gdk.color_parse(self.active_color)
        (red2, green2, blue2) = (color.red, color.green, color.blue)
        red = red1 + int(self.fade_level * abs(red1 - red2))
        green = green1 + int(self.fade_level * abs(green1 - green2))
        blue = blue1 + int(self.fade_level * abs(blue1 - blue2))
        self.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(red, green, blue))
        self.fade_level -= 1.0 / (self.fade_duration / 25)
        if self.fade_level > 0:
            return True
        self.idle = 0
        return False
