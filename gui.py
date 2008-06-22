# -*- coding: utf-8 -*-

"""
    PyRoom - A clone of WriteRoom
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Basic global GUI

    :copyright: 2007 Nicolas P. Rougier & NoWhereMan Copyright
    :copyright: 2008 The PyRoom Theme - See AUTHORS file for more information
    :license: GNU General Public License, version 3 or later
"""

from status_label import FadeLabel

import gtk
import pango
import gtksourceview
import gtk.glade
import ConfigParser
import os


class GUI():

    def __init__(self, style, verbose, pyroom_config):
        self.verbose = verbose
        self.status = FadeLabel()
        self.error = FadeLabel()
        self.style = style

        # Main window

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_name('PyRoom')
        self.window.set_title("PyRoom")
        self.window.connect('delete_event', self.delete_event)
        self.window.connect('destroy', self.destroy)

        self.textbox = gtksourceview.SourceView()
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
        self.vbox.pack_start(self.boxout, True, True, 6)
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

        # Error
        self.hbox2 = gtk.HBox()
        self.hbox2.set_spacing(12)
        self.hbox2.pack_end(self.error, True, True, 0)
        self.vbox.pack_end(self.hbox2, False, False, 0)
        self.error.set_alignment(0.0, 0.5)
        self.error.set_justify(gtk.JUSTIFY_LEFT)

        # Status
        self.hbox = gtk.HBox()
        self.hbox.set_spacing(12)
        self.hbox.pack_end(self.status, True, True, 0)
        self.vbox.pack_end(self.hbox, False, False, 0)
        self.status.set_alignment(0.0, 0.5)
        self.status.set_justify(gtk.JUSTIFY_LEFT)


        self.config = ConfigParser.ConfigParser()
        if self.style:
            theme = os.path.join(pyroom_config.conf_dir, 'themes',
                                 style + ".theme")
        else:
            theme = os.path.join(pyroom_config.conf_dir, 'themes',
            pyroom_config.config.get("visual", "theme") + ".theme")
        self.config.read(theme)

    def quit(self):
        """ quit pyroom """
        gtk.main_quit()

    def delete_event(self, widget, event, data=None):
        """ Quit """
        return False

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

    def apply_style(self, style=None, mode='normal'):
        if mode == 'normal':
            self.window.modify_bg(gtk.STATE_NORMAL,
                                  gtk.gdk.color_parse(self.config.get("theme",
                                                      "background")))
            self.textbox.modify_bg(gtk.STATE_NORMAL,
                                   gtk.gdk.color_parse(self.config.get(
                                               "theme", "background")))
            self.textbox.modify_base(gtk.STATE_NORMAL,
                                     gtk.gdk.color_parse(self.config.get(
                                                 "theme", "background")))
            self.textbox.modify_base(gtk.STATE_SELECTED,
                                     gtk.gdk.color_parse(self.config.get(
                                                 "theme", "foreground")))
            self.textbox.modify_text(gtk.STATE_NORMAL,
                                     gtk.gdk.color_parse(self.config.get(
                                                 "theme", "foreground")))
            self.textbox.modify_text(gtk.STATE_SELECTED,
                                     gtk.gdk.color_parse('#000000'))
            self.textbox.modify_fg(gtk.STATE_NORMAL,
                                   gtk.gdk.color_parse(self.config.get(
                                               "theme", "foreground")))
            self.status.active_color = self.config.get("theme", "foreground")
            self.status.inactive_color = self.config.get("theme", "background")
            self.error.active_color = self.config.get("theme", "foreground")
            self.error.inactive_color = self.config.get("theme", "background")
            self.boxout.modify_bg(gtk.STATE_NORMAL,
                                  gtk.gdk.color_parse(self.config.get(
                                                  "theme", "border")))
            font_and_size = '%s %d' % (self.config.get("theme", "font"),
                                       float(self.config.get("theme",
                                                        "fontsize")))
            self.textbox.modify_font(pango.FontDescription(font_and_size))

            gtk.rc_parse_string("""
            style "pyroom-colored-cursor" {
            GtkTextView::cursor-color = '"""
                                 + self.config.get("theme", "foreground")
                                 + """'
            }
            class "GtkWidget" style "pyroom-colored-cursor"
            """)
            (w, h) = (gtk.gdk.screen_width(), gtk.gdk.screen_height())
            width = int(float(self.config.get("theme", "width")) * w)
            height = int(float(self.config.get("theme", "height")) * h)
            self.vbox.set_size_request(width, height)
            self.fixed.move(self.vbox, int(((1 - float(self.config.get(
                                           "theme", "width"))) * w)/ 2),
                int(((1-float(self.config.get("theme", "height"))) * h) / 2))
            self.textbox.set_border_width(int(self.config.get(
                                         "theme", "padding")))
        elif mode == 'custom':
            self.style = style
            self.window.modify_bg(gtk.STATE_NORMAL,
                                  gtk.gdk.color_parse(self.style[
                                                  'background']))
            self.textbox.modify_bg(gtk.STATE_NORMAL,
                                   gtk.gdk.color_parse(self.style[
                                                   'background']))
            self.textbox.modify_base(gtk.STATE_NORMAL,
                                     gtk.gdk.color_parse(self.style[
                                                     'background']))
            self.textbox.modify_base(gtk.STATE_SELECTED,
                                     gtk.gdk.color_parse(self.style[
                                                     'foreground']))
            self.textbox.modify_text(gtk.STATE_NORMAL,
                                     gtk.gdk.color_parse(self.style[
                                                     'foreground']))
            self.textbox.modify_text(gtk.STATE_SELECTED,
                                     gtk.gdk.color_parse('#000000'))
            self.textbox.modify_fg(gtk.STATE_NORMAL,
                                   gtk.gdk.color_parse(self.style[
                                                   'foreground']))
            self.status.active_color = self.style['foreground']
            self.status.inactive_color = self.style['background']
            self.boxout.modify_bg(gtk.STATE_NORMAL,
                                  gtk.gdk.color_parse(self.style['border']))
            font_and_size = '%s %d' % (self.style['font'],
                                       float(self.style['fontsize']))
            self.textbox.modify_font(pango.FontDescription(font_and_size))

            gtk.rc_parse_string("""
            style "pyroom-colored-cursor" {
            GtkTextView::cursor-color = '"""
                                 + self.style['foreground']
                                 + """'
            }
            class "GtkWidget" style "pyroom-colored-cursor"
            """)
            (w, h) = (gtk.gdk.screen_width(), gtk.gdk.screen_height())
            width = int(self.style['size'][0] * w)
            height = int(self.style['size'][1] * h)
            self.vbox.set_size_request(width, height)
            self.fixed.move(self.vbox, int(((1 - self.style['size'][0])
                                                              * w)/ 2),
                int(((1 - self.style['size'][1]) * h) / 2))
            self.textbox.set_border_width(self.style['padding'])
