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
basic global GUI

Additionally allows user to apply custom settings
"""

import gtk
import gobject
import pango
import gtk.glade
import ConfigParser
import os
from sys import platform
if platform == 'win32':
    data_home = os.environ['APPDATA']
else:
    from xdg.BaseDirectory import xdg_data_home as data_home

from pyroom_error import PyroomError

class Theme(dict):
    """basically a dict with some utility methods"""
    def __init__(self, theme_name):
        theme_filename = self._lookup_theme(theme_name)
        if not theme_filename:
            raise PyroomError(_('theme not found: %s') % theme_name)
        theme_file = ConfigParser.SafeConfigParser()
        theme_file.read(theme_filename)
        self.update(theme_file.items('theme'))

    def _lookup_theme(self, theme_name):
        """lookup theme_filename for given theme_name

        order of preference is homedir, global dir, source dir (if available)"""
        local_directory = os.path.join(data_home, 'pyroom', 'themes')
        global_directory = '/usr/share/pyroom/themes' # FIXME: platform
        # in case PyRoom is run without installation
        fallback_directory = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..',
            'themes'
        )
        for dirname in (local_directory, global_directory, fallback_directory):
            filename = os.path.join(dirname, theme_name + '.theme')
            if os.path.isfile(filename):
                return filename

    def save(self, filename):
        """save a theme"""
        theme_file = ConfigParser.SafeConfigParser()
        theme_file.add_section('theme')
        for key, value in self.iteritems():
            theme_file.set('theme', key, str(value))
        theme_file.set('theme', 'name', os.path.basename(filename))
        theme_file.write(open(filename + '.theme', 'w'))

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
        red = red1 + int(self.fade_level * (red2 - red1))
        green = green1 + int(self.fade_level * (green2 - green1))
        blue = blue1 + int(self.fade_level * (blue2 - blue1))
        self.modify_fg(gtk.STATE_NORMAL, gtk.gdk.Color(red, green, blue))
        self.fade_level -= 1.0 / (self.fade_duration / 25)
        if self.fade_level > 0:
            return True
        self.idle = 0
        return False

class GUI(object):
    """our basic global gui object"""

    def __init__(self, pyroom_config, edit_instance):
        self.config = pyroom_config.config # FIXME: use pyroom_config itself
        # Theme
        theme_name = self.config.get('visual', 'theme')
        self.theme = Theme(theme_name)

        self.status = FadeLabel()
        self.edit_instance = edit_instance
        
        # Main window

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_name('PyRoom')
        self.window.set_title("PyRoom")
        self.window.connect('delete_event', self.delete_event)
        self.window.connect('destroy', self.destroy)

        self.textbox = gtk.TextView()
        self.textbox.connect('scroll-event', self.scroll_event)
        self.textbox.set_wrap_mode(gtk.WRAP_WORD)

        self.fixed = gtk.Fixed()
        self.vbox = gtk.VBox()
        self.window.add(self.fixed)
        self.fixed.put(self.vbox, 0, 0)

        self.boxout = gtk.EventBox()
        self.boxout.set_border_width(1)
        self.boxin = gtk.EventBox()
        self.boxin.set_border_width(1)
        self.vbox.pack_start(self.boxout, True, True, 1)
        self.boxout.add(self.boxin)

        self.scrolled = gtk.ScrolledWindow()
        self.boxin.add(self.scrolled)
        self.scrolled.add(self.textbox)
        self.scrolled.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        self.scrolled.show()
        self.scrolled.set_property('resize-mode', gtk.RESIZE_PARENT)
        self.textbox.set_property('resize-mode', gtk.RESIZE_PARENT)
        self.vbox.set_property('resize-mode', gtk.RESIZE_PARENT)
        self.vbox.show_all()

        # Status
        self.hbox = gtk.HBox()
        self.hbox.set_spacing(12)
        self.hbox.pack_end(self.status, True, True, 0)
        self.vbox.pack_end(self.hbox, False, False, 0)
        self.status.set_alignment(0.0, 0.5)
        self.status.set_justify(gtk.JUSTIFY_LEFT)
        
        self.apply_theme()

    def apply_theme(self):
        """immediately apply the theme given in configuration

        this has changed from previous versions! Takes no arguments!
        Only uses configuration!"""
        
        # text cursor
        gtkrc_string = """\
        style "pyroom-colored-cursor" { 
        GtkTextView::cursor-color = '%s'
        bg_pixmap[NORMAL] = "<none>"
        }
        class "GtkWidget" style "pyroom-colored-cursor"
        """ % self.theme['foreground']
        gtk.rc_parse_string(gtkrc_string)

        padding = int(self.theme['padding'])
        self.textbox.set_border_width(padding)
        
        # Screen geometry
        screen = gtk.gdk.screen_get_default() 
        root_window = screen.get_root_window() 
        mouse_x, mouse_y, mouse_mods = root_window.get_pointer()
        current_monitor_number = screen.get_monitor_at_point(mouse_x, mouse_y)
        monitor_geometry = screen.get_monitor_geometry(current_monitor_number)
        (screen_width, screen_height) = (monitor_geometry.width,
                                         monitor_geometry.height)

        width_percentage = float(self.theme['width'])
        height_percentage = float(self.theme['height'])
        
        # Sizing
        self.vbox.set_size_request(
            int(width_percentage * screen_width),
            int(height_percentage * screen_height)
        )
        self.fixed.move(self.vbox,
                        int(((1 - width_percentage) * screen_width) / 2),
                        int(((1 - height_percentage) * screen_height) / 2)
                       )

        parse_color = lambda x: gtk.gdk.color_parse(self.theme[x])
        # Colors
        self.window.modify_bg(gtk.STATE_NORMAL, parse_color('background'))
        self.boxout.modify_bg(gtk.STATE_NORMAL, parse_color('border'))
        self.status.active_color = self.theme['foreground']
        self.status.inactive_color = self.theme['background']
        self.textbox.modify_bg(gtk.STATE_NORMAL, parse_color('textboxbg'))
        self.textbox.modify_base(gtk.STATE_NORMAL, parse_color('textboxbg'))
        self.textbox.modify_base(gtk.STATE_SELECTED, parse_color('foreground'))
        self.textbox.modify_text(gtk.STATE_NORMAL, parse_color('foreground'))
        self.textbox.modify_text(gtk.STATE_SELECTED, parse_color('textboxbg'))
        self.textbox.modify_fg(gtk.STATE_NORMAL, parse_color('foreground'))

        # Border
        if not int(self.config.get('visual', 'showborder')):
            self.boxin.set_border_width(0)
            self.boxout.set_border_width(0)
        else:
            self.boxin.set_border_width(1)
            self.boxout.set_border_width(1)

        # Indent
        if self.config.get('visual', 'indent') == '1':
            pango_context = self.textbox.get_pango_context()
            current_font_size = pango_context.\
                    get_font_description().\
                    get_size() / 1024
            self.textbox.set_indent(current_font_size * 2)
        else:
            self.textbox.set_indent(0)

    def quit(self):
        """ quit pyroom """
        gtk.main_quit()

    def delete_event(self, widget, event, data=None):
        """ Quit """
        self.edit_instance.dialog_quit()
        return True

    def destroy(self, widget, data=None):
        """ Quit """
        gtk.main_quit()

    def scroll_event(self, widget, event):
        """ Scroll event dispatcher """

        if event.direction == gtk.gdk.SCROLL_UP:
            self.scroll_up()
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            self.scroll_down()

    def scroll_down(self):
        """ Scroll window down """

        adj = self.scrolled.get_vadjustment()
        if adj.upper > adj.page_size:
            adj.value = min(adj.upper - adj.page_size, adj.value
                             + adj.step_increment)

    def scroll_up(self):
        """ Scroll window up """

        adj = self.scrolled.get_vadjustment()
        if adj.value > adj.step_increment:
            adj.value -= adj.step_increment
        else:
            adj.value = 0
