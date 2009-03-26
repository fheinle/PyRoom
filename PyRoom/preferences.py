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
allows for custom set preferences

Creates a preferences UI that allows the user to customise settings; allows for
the choice of a theme from $XDG_DATA_HOME/pyroom/themes as well as a custom
theme created via the dialog
"""

import gtk
import gtk.glade
import pango
import os
from ConfigParser import SafeConfigParser, NoOptionError
from sys import platform
if platform == 'win32':
    data_home, config_home = (os.environ['APPDATA'],) * 2
else:
    from xdg.BaseDirectory import xdg_config_home as config_home
    from xdg.BaseDirectory import xdg_data_home as data_home

from gui import Theme
from pyroom_error import PyroomError
import autosave

DEFAULT_CONF = {
    'visual':{
        'theme':'green',
        'showborder':'1',
        'linespacing':'2',
        'custom_font':'Sans 12',
        'use_font_type':'custom',
        'indent':0,
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

    XXX: we really really should come up with a preferences system that is
    sane on a more global level
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

            
class PyroomConfig(object):
    """Fetches (and/or) builds basic configuration files/dirs."""

    def __init__(self):
        self.pyroom_absolute_path = os.path.dirname(os.path.abspath(__file__))
        self.conf_dir = os.path.join(config_home, 'pyroom')
        self.data_dir = os.path.join(data_home, 'pyroom')
        self.themes_dir  = os.path.join(self.data_dir, 'themes')
        self.global_themes_dir = '/usr/share/pyroom/themes'
        # if we are not using a global installation,
        # take the themes directly from sources
        if not os.path.isdir(self.global_themes_dir) :
            if platform == 'win32':
                self.global_themes_dir = ''
            else:
                self.global_themes_dir = os.path.join(
                    self.pyroom_absolute_path,
                    '..',
                    'themes'
                )
        self.conf_file = os.path.join(self.conf_dir, 'pyroom.conf')
        self.config = FailsafeConfigParser()
        self.build_default_conf()
        self.config.readfp(open(self.conf_file, 'r'))
        self.themeslist = self.read_themes_list()
        self.showborderstate = self.config.get('visual', 'showborder')

    def build_default_conf(self):
        """builds necessary default conf.
        * makes directories if not here,
        * copies theme data
        * builds the default conf file
        """
        if not os.path.isdir(self.conf_dir):
            os.makedirs(self.conf_dir)
            for section, settings in DEFAULT_CONF.items():
                self.config.add_section(section)
                for key, value in settings.items():
                    self.config.set(section, key, str(value))
            config_file = open(self.conf_file, "w")
            self.config.write(config_file)
            config_file.close()
        if not os.path.isdir(self.themes_dir):
            os.makedirs(os.path.join(self.themes_dir))

    def read_themes_list(self):
        """get all the theme files sans file suffix and the custom theme"""
        themeslist = []
        rawthemeslist = os.listdir(self.themes_dir)
        globalthemeslist = os.listdir(self.global_themes_dir)
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


class Preferences(object):
    """our main preferences object, to be passed around where needed"""
    def __init__(self, gui, pyroom_config):
        self.pyroom_config = pyroom_config
        self.config = self.pyroom_config.config
        self.graphical = gui
        self.wTree = gtk.glade.XML(os.path.join(
            pyroom_config.pyroom_absolute_path, "interface.glade"),
            "dialog-preferences")

        self.gnome_fonts = self.get_gnome_fonts()
        # Defining widgets needed
        self.window = self.wTree.get_widget("dialog-preferences")
        self.colorpreference = self.wTree.get_widget("colorbutton")
        self.textboxbgpreference = self.wTree.get_widget("textboxbgbutton")
        self.bgpreference = self.wTree.get_widget("bgbutton")
        self.borderpreference = self.wTree.get_widget("borderbutton")
        self.paddingpreference = self.wTree.get_widget("paddingtext")
        self.heightpreference = self.wTree.get_widget("heighttext")
        self.heightpreference.set_range(5, 95)
        self.widthpreference = self.wTree.get_widget("widthtext")
        self.widthpreference.set_range(5, 95)
        self.presetscombobox = self.wTree.get_widget("presetscombobox")
        self.showborderbutton = self.wTree.get_widget("showborder")
        self.autosave = self.wTree.get_widget("autosavetext")
        self.autosave_spinbutton = self.wTree.get_widget("autosavetime")
        self.linespacing_spinbutton = self.wTree.get_widget("linespacing")
        self.indent_check = self.wTree.get_widget("indent_check")
        if self.config.get('visual', 'indent') == '1':
            self.indent_check.set_active(True)
        self.save_custom_button = self.wTree.get_widget("save_custom_theme")
        self.custom_font_preference = self.wTree.get_widget("fontbutton1")
        if not self.config.get('visual', 'use_font_type') == 'custom':
            self.custom_font_preference.set_sensitive(False)
        self.font_radios = {
            'document':self.wTree.get_widget("radio_document_font"),
            'monospace':self.wTree.get_widget("radio_monospace_font"),
            'custom':self.wTree.get_widget("radio_custom_font")
        }
        for widget in self.font_radios.values():
            if not widget.get_name() == 'radio_custom_font':
                widget.set_sensitive(bool(self.gnome_fonts))

        # Setting up config parser
        self.customfile = FailsafeConfigParser()
        self.customfile.read(os.path.join(
            self.pyroom_config.themes_dir,'custom.theme')
        )
        if not self.customfile.has_section('theme'):
            self.customfile.add_section('theme')

        # Getting preferences from conf file
        self.activestyle = self.config.get("visual", "theme")
        self.pyroom_config.showborderstate = self.config.get(
            "visual", "showborder"
        )
        self.autosavestate = self.config.get("editor", "autosave")
        if int(self.autosavestate) == 1:
            self.autosave_time = self.config.get("editor", "autosavetime")
        else:
            self.autosave_time = 0
        self.linespacing = self.config.get("visual", "linespacing")
        self.pyroom_config.showborderstate = int(
            self.pyroom_config.showborderstate
        )
        self.autosavestate = int(self.autosavestate)

        # Set up pyroom from conf file
        self.linespacing_spinbutton.set_value(int(self.linespacing))
        self.autosave_spinbutton.set_value(float(self.autosave_time))
        self.autosave.set_active(self.autosavestate)
        self.showborderbutton.set_active(self.pyroom_config.showborderstate)
        font_type = self.config.get('visual', 'use_font_type')
        self.font_radios[font_type].set_active(True)
        
        self.toggleautosave(self.autosave)

        self.window.set_transient_for(self.graphical.window)

        self.stylesvalues = {'custom': 0}
        self.startingvalue = 1


        self.graphical.theme = Theme(self.config.get('visual', 'theme'))
        # Add themes to combobox
        for i in self.pyroom_config.themeslist:
            self.stylesvalues['%s' % (i)] = self.startingvalue
            self.startingvalue = self.startingvalue + 1
            current_loading_theme = Theme(i)
            theme_name = current_loading_theme['name']
            self.presetscombobox.append_text(theme_name)
        if self.activestyle == 'custom':
            self.save_custom_button.set_sensitive(True)
        self.presetscombobox.set_active(self.stylesvalues[self.activestyle])
        self.fill_pref_dialog()

        # Connecting interface's signals
        dic = {
                "on_MainWindow_destroy": self.QuitEvent,
                "on_button-ok_clicked": self.set_preferences,
                "on_button-close_clicked": self.kill_preferences,
                "on_close": self.kill_preferences
                }
        self.wTree.signal_autoconnect(dic)
        self.showborderbutton.connect('toggled', self.toggleborder)
        self.autosave.connect('toggled', self.toggleautosave)
        self.autosave_spinbutton.connect('value-changed', self.toggleautosave)
        self.linespacing_spinbutton.connect(
            'value-changed', self.changelinespacing
        )
        self.indent_check.connect(
            'toggled', self.toggle_indent
        )
        self.presetscombobox.connect('changed', self.presetchanged)
        self.colorpreference.connect('color-set', self.customchanged)
        self.textboxbgpreference.connect('color-set', self.customchanged)
        self.bgpreference.connect('color-set', self.customchanged)
        self.borderpreference.connect('color-set', self.customchanged)
        self.paddingpreference.connect('value-changed', self.customchanged)
        self.heightpreference.connect('value-changed', self.customchanged)
        self.widthpreference.connect('value-changed', self.customchanged)
        self.save_custom_button.connect('clicked', self.save_custom_theme)
        for widget in self.font_radios.values():
            widget.connect('toggled', self.change_font)
        self.custom_font_preference.connect('font-set', self.change_font)
        self.set_font()

    def get_gnome_fonts(self):
        """test if gnome font settings exist"""
        try:
            import gconf
        except ImportError:
            return
        gconf_client = gconf.Client()
        fonts = {'document':'', 'monospace':''}
        try:
            for font in fonts.keys():
                fonts[font] = gconf_client.get_value(
                    '/desktop/gnome/interface/%s_font_name' % 
                    font
                )
        except ValueError:
            return
        else:
            return fonts

    def change_font(self, widget):
        if widget.get_name() in ('fontbutton1', 'radio_custom_font'):
            self.custom_font_preference.set_sensitive(True)
            new_font = self.custom_font_preference.get_font_name()
            self.config.set('visual', 'use_font_type', 'custom')
            self.config.set('visual', 'custom_font', new_font)
        else:
            self.custom_font_preference.set_sensitive(False)
            font_type = widget.get_name().split('_')[1]
            self.config.set('visual', 'use_font_type', font_type)
        self.set_font()
        self.graphical.apply_theme()
    
    def set_font(self):
        """set font according to settings"""
        if self.config.get('visual', 'use_font_type') == 'custom' or\
           not self.gnome_fonts:
            new_font = self.config.get('visual', 'custom_font')
        else:
            font_type = self.config.get('visual', 'use_font_type')
            new_font = self.gnome_fonts[font_type]
        self.graphical.textbox.modify_font(pango.FontDescription(new_font))
        
    def getcustomdata(self):
        """reads custom themes"""
        self.colorname = gtk.gdk.Color.to_string(
                                self.colorpreference.get_color())
        self.textboxbgname = gtk.gdk.Color.to_string(
                                self.textboxbgpreference.get_color())
        self.bgname = gtk.gdk.Color.to_string(
                               self.bgpreference.get_color())
        self.bordername = gtk.gdk.Color.to_string(
                               self.borderpreference.get_color())
        self.paddingname = self.paddingpreference.get_value_as_int()
        self.heightname = self.heightpreference.get_value() / 100.0
        self.widthname = self.widthpreference.get_value() / 100.0

    def save_custom_theme(self, widget, data=None):
        chooser = gtk.FileChooserDialog('PyRoom', self.window, 
            gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
            gtk.STOCK_SAVE, gtk.RESPONSE_OK)
        )
        chooser.set_default_response(gtk.RESPONSE_OK)
        chooser.set_current_folder(self.pyroom_config.themes_dir)
        filter_pattern = gtk.FileFilter()
        filter_pattern.add_pattern('*.theme')
        filter_pattern.set_name(_('Theme Files'))
        chooser.add_filter(filter_pattern)
        res = chooser.run()
        if res == gtk.RESPONSE_OK:
            theme_filename = chooser.get_filename()
            self.graphical.theme.save(theme_filename)
            theme_name = os.path.basename(theme_filename)
            theme_id = max(self.stylesvalues.values()) + 1
            self.presetscombobox.append_text(theme_name)
            self.stylesvalues.update({theme_name: theme_id})
            self.presetscombobox.set_active(theme_id)
        chooser.destroy()

    def set_preferences(self, widget, data=None):
        """save preferences"""
        self.getcustomdata()
        self.autosavepref = self.autosave.get_active()
        if self.autosavepref == True:
            self.autosavepref = 1
        else:
            self.autosavepref = 0
        self.config.set("editor", "autosave", str(self.autosavepref))
        self.config.set("visual", "linespacing", str(int(self.linespacing)))

        autosave_time = self.autosave_spinbutton.get_value_as_int()
        self.config.set("editor", "autosavetime", str(autosave_time))

        if self.presetscombobox.get_active_text().lower() == 'custom':
            custom_theme = open(os.path.join(
                self.pyroom_config.themes_dir, 'custom.theme'),
                "w"
            )
            self.customfile.set("theme", "background", self.bgname)
            self.customfile.set("theme", "foreground", self.colorname)
            self.customfile.set("theme", "textboxbg", self.textboxbgname)
            self.customfile.set("theme", "border", self.bordername)
            self.customfile.set("theme", "padding", str(self.paddingname))
            self.customfile.set("theme", "width", str(self.widthname))
            self.customfile.set("theme", "height", str(self.heightname))
            self.customfile.write(custom_theme)
        self.dlg.hide()
        try:
            config_file = open(os.path.join(self.pyroom_config.conf_dir,
                                            "pyroom.conf"), "w")
            self.config.write(config_file)
        except IOError:
            raise PyroomError(_("Could not save preferences file."))
            
    def customchanged(self, widget):
        """triggered when custom themes are changed, reloads style"""
        self.presetscombobox.set_active(0)
        self.presetchanged(widget)

    def fill_pref_dialog(self):
        self.custom_font_preference.set_font_name(
            self.config.get('visual', 'custom_font')
        )
        parse_color = lambda x: gtk.gdk.color_parse(
            self.graphical.theme[x]
        )
        self.colorpreference.set_color(parse_color('foreground'))
        self.textboxbgpreference.set_color(parse_color('textboxbg'))
        self.bgpreference.set_color(parse_color('background'))
        self.borderpreference.set_color(parse_color('border'))
        self.paddingpreference.set_value(float(
            self.graphical.theme['padding'])
        )
        self.widthpreference.set_value(
            float(self.graphical.theme['width']) * 100
        )
        self.heightpreference.set_value(
            float(self.graphical.theme['height']) * 100
        )

    def presetchanged(self, widget, mode=None):
        """some presets have changed, apply those"""
        active_theme_id = self.presetscombobox.get_active()
        for key, value in self.stylesvalues.iteritems():
            if value == active_theme_id:
                active_theme = key
        if active_theme_id == 0:
            self.getcustomdata()
            custom_theme = Theme('custom')
            custom_theme.update({
                    'name': 'custom',
                    'background': self.bgname,
                    'textboxbg': self.textboxbgname,
                    'foreground': self.colorname,
                    'lines': self.colorname,
                    'border': self.bordername,
                    'info': self.colorname,
                    'padding': self.paddingname,
                    'height': self.heightname,
                    'width': self.widthname,
            })

            self.config.set("visual", "theme", str(active_theme))
            self.graphical.theme = custom_theme
            self.save_custom_button.set_sensitive(True)
        else:
            new_theme = Theme(active_theme)
            self.graphical.theme = new_theme
            parse_color = lambda x: gtk.gdk.color_parse(
                self.graphical.theme[x]
            )
            self.colorpreference.set_color(parse_color('foreground'))
            self.textboxbgpreference.set_color(parse_color('textboxbg'))
            self.bgpreference.set_color(parse_color('background'))
            self.borderpreference.set_color(parse_color('border'))
            self.paddingpreference.set_value(float(
                self.graphical.theme['padding'])
            )
            self.widthpreference.set_value(
                float(self.graphical.theme['width']) * 100
            )
            self.heightpreference.set_value(
                float(self.graphical.theme['height']) * 100
            )
            self.config.set("visual", "theme", str(active_theme))
            self.presetscombobox.set_active(active_theme_id)
            self.save_custom_button.set_sensitive(False)

        self.graphical.apply_theme()
        self.graphical.status.set_text(_('Style Changed to %s') %
                                        (active_theme))

    def show(self):
        """display the preferences dialog"""
        self.dlg = self.wTree.get_widget("dialog-preferences")
        self.dlg.show()

    def toggle_indent(self, widget):
        """toggle textbox indent"""
        if self.config.get('visual', 'indent') == '1':
            self.config.set('visual', 'indent', '0')
        else:
            self.config.set('visual', 'indent', '1')
        self.graphical.apply_theme()

    def toggleborder(self, widget):
        """toggle border display"""
        #FIXME just workaround, we should drop pyroom_config entirely
        if self.pyroom_config.showborderstate:
            self.pyroom_config.showborderstate = 0
            self.config.set('visual', 'showborder', '0')
        else:
            self.pyroom_config.showborderstate = 1
            self.config.set('visual', 'showborder', '1')
        self.graphical.boxout.set_border_width(
            self.pyroom_config.showborderstate
        )
        self.graphical.boxin.set_border_width(
            self.pyroom_config.showborderstate
        )

    def changelinespacing(self, widget):
        """Change line spacing"""
        self.linespacing = self.linespacing_spinbutton.get_value()
        self.graphical.textbox.set_pixels_below_lines(int(self.linespacing))
        self.graphical.textbox.set_pixels_above_lines(int(self.linespacing))
        self.graphical.textbox.set_pixels_inside_wrap(int(self.linespacing))
        

    def toggleautosave(self, widget):
        """enable or disable autosave"""
        if self.autosave.get_active():
            self.autosave_spinbutton.set_sensitive(True)
            self.autosave_time = self.autosave_spinbutton.get_value_as_int()
        else:
            self.autosave_spinbutton.set_sensitive(False)
            self.autosave_time = 0

    def QuitEvent(self, widget, data=None):
        """quit our app"""
        gtk.main_quit()
        return False

    def kill_preferences(self, widget, data=None):
        """hide the preferences window"""
        self.dlg.hide()
        return True
