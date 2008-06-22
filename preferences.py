# -*- coding: utf-8 -*-

"""
    PyRoom - A clone of WriteRoom
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Preferences

    :copyright: 2007 Nicolas P. Rougier & NoWhereMan Copyright
    :copyright: 2008 The PyRoom Theme - See AUTHORS file for more information
    :license: GNU General Public License, version 3 or later
"""

import gtk
import gtk.glade
import os
from pyroom_error import PyroomError
import autosave
import ConfigParser
import shutil


DEFAULT_CONF = """
[visual]
theme = green
linenumber = 0

[editor]
session = True
autosavetime = 2
autosave = 0
"""


class PyroomConfig():
    """Fetches (and/or) builds basic configuration files/dirs."""

    def __init__(self):
        self.pyroom_absolute_path = os.path.dirname(os.path.abspath(__file__))
        home = os.getenv("HOME")
        self.conf_dir = os.path.join(home, '.pyroom')
        self.conf_file = os.path.join(self.conf_dir, 'pyroom.conf')
        self.build_default_conf()
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.conf_file)
        self.themeslist = self.read_themes_list()

    def build_default_conf(self):
        """builds necessary default conf.
        * makes directories if not here,
        * copies theme data
        * builds the default conf file
        """
        if not os.path.isdir(self.conf_dir):
            os.mkdir(self.conf_dir)
        if not os.path.isdir(os.path.join(self.conf_dir, 'themes')):
            os.mkdir(os.path.join(self.conf_dir, 'themes'))
        if not os.path.isfile(self.conf_file):
            config_file = open(self.conf_file, "w")
            config_file.write(DEFAULT_CONF)
            config_file.close()
        # Copy themes
        theme_source_dir = os.path.join(self.pyroom_absolute_path, 'themes/')
        for theme_file in os.listdir(theme_source_dir):
            if theme_file != 'custom.theme':
                shutil.copy(
                    os.path.join(theme_source_dir, theme_file),
                    os.path.join(self.conf_dir, "themes/"))

    def read_themes_list(self):
        """get all the theme files sans file suffix and the custom theme"""
        themeslist = []
        rawthemeslist = os.listdir(os.path.join(self.conf_dir, "themes/"))
        for themefile in rawthemeslist:
            if themefile.endswith('theme') and themefile != 'custom.theme':
                themeslist.append(themefile[:-6])
        return themeslist


class Preferences():
    """our main preferences object, to be passed around where needed"""
    def __init__(self, gui, style, verbose, pyroom_config):
        self.style = style
        self.pyroom_config = pyroom_config
        self.wTree = gtk.glade.XML(os.path.join(
            pyroom_config.pyroom_absolute_path, "interface.glade"),
            "dialog-preferences")
        self.window = self.wTree.get_widget("dialog-preferences")
        self.fontpreference = self.wTree.get_widget("fontbutton")
        self.colorpreference = self.wTree.get_widget("colorbutton")
        self.bgpreference = self.wTree.get_widget("bgbutton")
        self.borderpreference = self.wTree.get_widget("borderbutton")
        self.paddingpreference = self.wTree.get_widget("paddingtext")
        self.heightpreference = self.wTree.get_widget("heighttext")
        self.widthpreference = self.wTree.get_widget("widthtext")
        self.presetscombobox = self.wTree.get_widget("presetscombobox")
        self.linenumbers = self.wTree.get_widget("linescheck")
        self.autosave = self.wTree.get_widget("autosavetext")
        self.autosave_spinbutton = self.wTree.get_widget("autosavetime")
        self.graphical = gui

        self.customfile = ConfigParser.ConfigParser()
        self.customfile.read(os.path.join(self.pyroom_config.conf_dir,
            "themes/custom.theme"))
        if not self.customfile.has_section('theme'):
            self.customfile.add_section('theme')

        self.config = self.pyroom_config.config

        self.activestyle = self.config.get("visual", "theme")
        self.linesstate = self.config.get("visual", "linenumber")
        self.autosavestate = self.config.get("editor", "autosave")
        self.autosavetime = self.config.get("editor", "autosavetime")
        if self.autosavestate == 1:
            autosave.autosave_time = self.autosavetime
        else:
            autosave.autosave_time = 0
        self.autosave_spinbutton.set_value(float(self.autosavetime))
        self.linesstate = int(self.linesstate)
        self.autosavestate = int(self.autosavestate)
        self.verbose = verbose

        self.linenumbers.set_active(self.linesstate)
        self.autosave.set_active(self.autosavestate)
        self.toggleautosave(self.autosave)

        self.window.set_transient_for(self.graphical.window)

        self.stylesvalues = {'custom': 0}
        self.startingvalue = 1

        for i in self.pyroom_config.themeslist:
            self.stylesvalues['%s' % (i)] = self.startingvalue
            self.startingvalue = self.startingvalue + 1
            i = i.capitalize()
            self.presetscombobox.append_text(i)
        self.presetscombobox.set_active(self.stylesvalues[self.activestyle])
        self.presetchanged(self.presetscombobox, 'initial')

        # Connecting interface's signals
        dic = {
                "on_MainWindow_destroy": self.QuitEvent,
                "on_button-ok_clicked": self.set_preferences,
                "on_button-close_clicked": self.kill_preferences,
                }
        self.wTree.signal_autoconnect(dic)
        self.linenumbers.connect('toggled', self.togglelines)
        self.autosave.connect('toggled', self.toggleautosave)
        self.autosave_spinbutton.connect('value-changed', self.toggleautosave)
        self.presetscombobox.connect('changed', self.presetchanged)
        self.fontpreference.connect('font-set', self.customchanged)
        self.colorpreference.connect('color-set', self.customchanged)
        self.bgpreference.connect('color-set', self.customchanged)
        self.borderpreference.connect('color-set', self.customchanged)
        self.paddingpreference.connect('value-changed', self.customchanged)
        self.heightpreference.connect('value-changed', self.customchanged)
        self.widthpreference.connect('value-changed', self.customchanged)

    def getcustomdata(self):
        """reads custom themes"""
        self.fontname = self.fontpreference.get_font_name()
        self.fontsize = int(self.fontname[-2:])
        self.fontname = self.fontname[:-2]
        self.colorname = self.format_rgb(gtk.gdk.Color.to_string(
                                self.colorpreference.get_color()))
        self.bgname = self.format_rgb(gtk.gdk.Color.to_string(
                               self.bgpreference.get_color()))
        self.bordername = self.format_rgb(gtk.gdk.Color.to_string(
                               self.borderpreference.get_color()))
        self.paddingname = self.paddingpreference.get_value_as_int()
        self.heightname = self.heightpreference.get_value()
        self.widthname = self.widthpreference.get_value()

    def set_preferences(self, widget, data=None):
        """save preferences"""
        self.getcustomdata()
        self.linenumberspref = self.linenumbers.get_active()
        self.autosavepref = self.autosave.get_active()
        if self.linenumberspref == True:
            self.linenumberspref = 1
        else:
            self.linenumberspref = 0
        if self.autosavepref == True:
            self.autosavepref = 1
        else:
            self.autosavepref = 0
        self.config.set("visual", "linenumber", self.linenumberspref)
        self.config.set("editor", "autosave", self.autosavepref)

        autosave.autosave_time = self.autosave_spinbutton.get_value_as_int()
        self.config.set("editor", "autosavetime", autosave.autosave_time)

        if self.presetscombobox.get_active_text().lower() == 'custom':
            custom_theme = open(os.path.join(self.pyroom_config.conf_dir,
                "themes/custom.theme"), "w")
            self.customfile.set("theme", "background", self.bgname)
            self.customfile.set("theme", "foreground", self.colorname)
            self.customfile.set("theme", "border", self.bordername)
            self.customfile.set("theme", "font", self.fontname)
            self.customfile.set("theme", "fontsize", self.fontsize)
            self.customfile.set("theme", "padding", self.paddingname)
            self.customfile.set("theme", "width", self.widthname)
            self.customfile.set("theme", "height", self.heightname)
            self.customfile.write(custom_theme)
        self.dlg.hide()
        try:
            config_file = open(os.path.join(self.pyroom_config.conf_dir, "pyroom.conf"),
                                                                         "w")
            self.config.write(config_file)
        except IOError:
            e = PyroomError(_("Could not save preferences file."))
            self.graphical.error.set_text(str(e))
            if self.verbose:
                print str(e)
                print e.traceback

    def customchanged(self, widget):
        """triggered when custom themes are changed, reloads style"""
        self.presetscombobox.set_active(0)
        self.presetchanged(widget)

    def presetchanged(self, widget, mode=None):
        """some presets have changed, apply those"""
        if mode == 'initial':
            self.graphical.apply_style(self.style, 'normal')
            self.fontname = "%s %s" % (self.graphical.config.get("theme", "font"),
                            self.graphical.config.get("theme", "fontsize"))
            self.fontpreference.set_font_name(self.fontname)
            self.colorpreference.set_color(gtk.gdk.color_parse(
             self.graphical.config.get("theme", "foreground")))
            self.bgpreference.set_color(gtk.gdk.color_parse(
             self.graphical.config.get("theme", "background")))
            self.borderpreference.set_color(gtk.gdk.color_parse(
                  self.graphical.config.get("theme", "border")))
            self.paddingpreference.set_value(float(self.graphical.config.get(
                                                        "theme", "padding")))
            self.widthpreference.set_value(float(self.graphical.config.get(
                                                        "theme", "width")))
            self.heightpreference.set_value(float(self.graphical.config.get(
                                                        "theme", "height")))
        else:
            active = self.presetscombobox.get_active_text().lower()
            activeid = self.presetscombobox.get_active()
            if activeid == 0:
                self.getcustomdata()
                customstyle = {
                    'Custom': {
                        'name': 'custom',
                        'background': self.bgname,
                        'foreground': self.colorname,
                        'lines': self.colorname,
                        'border': self.bordername,
                        'info': self.colorname,
                        'font': self.fontname,
                        'fontsize': self.fontsize,
                        'padding': self.paddingname,
                        'size': [self.widthname, self.heightname],
                }}
                self.graphical.apply_style(customstyle['Custom'], 'custom')
                self.graphical.apply_style(customstyle['Custom'], 'custom')
                self.config.set("visual", "theme", active)
                self.graphical.status.set_text(_('Style Changed to \
                                                %s' % (active)))
            else:
                theme = os.path.join(self.pyroom_config.conf_dir, "themes/",
                    active + ".theme")
                self.graphical.config.read(theme)
                self.graphical.apply_style()
                self.graphical.apply_style()
                self.fontname = "%s %s" % (self.graphical.config.get("theme", "font"),
                                    self.graphical.config.get("theme", "fontsize"))
                self.fontpreference.set_font_name(self.fontname)
                self.config.set("visual", "theme", active)
                self.colorpreference.set_color(gtk.gdk.color_parse(
                 self.graphical.config.get("theme", "foreground")))
                self.bgpreference.set_color(gtk.gdk.color_parse(
                 self.graphical.config.get("theme", "background")))
                self.borderpreference.set_color(gtk.gdk.color_parse(
                      self.graphical.config.get("theme", "border")))
                self.paddingpreference.set_value(float(
                 self.graphical.config.get("theme", "padding")))
                self.widthpreference.set_value(float(self.graphical.config.get(
                                                            "theme", "width")))
                self.heightpreference.set_value(float(
                 self.graphical.config.get("theme", "height")))
                self.graphical.status.set_text(_('Style Changed to \
%s' % (active)))
                self.presetscombobox.set_active(activeid)

    def show(self):
        """display the preferences dialog"""
        self.dlg = self.wTree.get_widget("dialog-preferences")
        self.dlg.show()

    def format_rgb(self, color):
        """rgb representation formatting"""
        color = color[0:3]+color[5:7]+color[11:13]
        color = color.upper()
        return color

    def togglelines(self, widget):
        """show line numbers"""
        opposite_state = not self.graphical.textbox.get_show_line_numbers()
        self.graphical.textbox.set_show_line_numbers(opposite_state)

    def toggleautosave(self, widget):
        """enable or disable autosave"""
        if self.autosave.get_active():
            self.autosave_spinbutton.set_sensitive(True)
            autosave.autosave_time = self.autosave_spinbutton.get_value_as_int()
        else:
            self.autosave_spinbutton.set_sensitive(False)
            autosave.autosave_time = 0

    def QuitEvent(self, widget, data=None):
        """quit our app"""
        gtk.main_quit()
        return False

    def kill_preferences(self, widget, data=None):
        """hide the preferences window"""
        self.dlg.hide()
