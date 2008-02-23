import gtk
import gtk.glade
import os.path
import styles
from status_label import FadeLabel
import ConfigParser

# this will be changed when styles are stored in external files
styleslist = ['green','darkgreen','blue','c64','locontrast','cupid','banker']

class Preferences():
    def __init__(self,gui,style,verbose):
        self.wTree = gtk.glade.XML("preferences.glade", "dialog-preferences")
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
        self.graphical = gui
        self.config = ConfigParser.ConfigParser()
        self.customfile = ConfigParser.ConfigParser()
        self.config.read("example.conf")
#        self.customfile.read("%s/.pyroom/custom.style" % (os.path.expanduser("~")))
#        self.custom = self.customfile.items("style")
        self.activestyle = self.config.get("style","theme")
        self.window.set_transient_for(self.graphical.window)

        self.stylesvalues = { 'Custom' : 0 }
        self.startingvalue = 1

        for i in styleslist:
            self.stylesvalues['%s' % (i)] = self.startingvalue
            self.startingvalue = self.startingvalue + 1
            i = i.capitalize()
            self.presetscombobox.append_text(i)
        self.presetscombobox.set_active(self.stylesvalues[self.activestyle])
        self.presetchanged(self.presetscombobox)

        # Connecting interface's signals
        dic = {
                "on_MainWindow_destroy" : self.QuitEvent,
                "on_button-ok_clicked" : self.set_preferences,
                "on_button-close_clicked" : self.kill_preferences,
                "on_linescheck_toggled" : self.togglelines
                }
        self.wTree.signal_autoconnect(dic)
        self.presetscombobox.connect('changed', self.presetchanged)
        self.fontpreference.connect('font-set', self.customchanged)
        self.colorpreference.connect('color-set', self.customchanged)
        self.bgpreference.connect('color-set', self.customchanged)
        self.borderpreference.connect('color-set', self.customchanged)
        self.paddingpreference.connect('value-changed', self.customchanged)
        self.heightpreference.connect('value-changed', self.customchanged)
        self.widthpreference.connect('value-changed', self.customchanged)

    def getcustomdata(self):
        self.fontname = self.fontpreference.get_font_name()
        self.fontsize = int(self.fontname[-2:])
        self.fontname = self.fontname[:-2]
        self.colorname = gtk.gdk.Color.to_string(self.colorpreference.get_color())
        self.bgname = gtk.gdk.Color.to_string(self.bgpreference.get_color())
        self.bordername = gtk.gdk.Color.to_string(self.borderpreference.get_color())
        self.paddingname = self.paddingpreference.get_value_as_int()
        self.heightname = self.heightpreference.get_value()
        self.widthname = self.widthpreference.get_value()

    def set_preferences(self, widget, data=None):
#        if active == 'Custom' or active == 'custom':
#             writing custom style to ~/.pyroom/custom.style
#            save = open("~/.pyroom/custom.style")
            
        self.preset = self.presetscombobox.get_active_text()
        self.dlg.hide()
        f = open("example.conf", "w")
        self.config.write(f)

    def customchanged(self, widget):
        self.presetscombobox.set_active(0)
        self.presetchanged(widget)

    def presetchanged(self, widget):
        active = self.presetscombobox.get_active_text().lower()
        activeid = self.presetscombobox.get_active()
        if active == 'Custom' or active == 'custom':
            self.getcustomdata()
            customstyle = {
                'Custom': {
                    'name': 'custom',
                    'background': self.bgname,
                    'foreground': self.colorname,
                    'lines': self.bordername,
                    'border': self.bordername,
                    'info': self.colorname,
                    'font': self.fontname,
                    'fontsize': self.fontsize,
                    'padding': self.paddingname,
                    'size': [self.widthname, self.heightname],
            }}
            self.graphical.apply_style(customstyle['Custom'])
            self.graphical.apply_style(customstyle['Custom'])
            self.graphical.status.set_text(_('Style Changed to %s' % (active)))
        else:
            self.graphical.apply_style(styles.styles[active])
            self.graphical.apply_style(styles.styles[active])
            self.style = styles.styles[active]
            self.fontname = self.style['font'] + ' ' + str(self.style['fontsize'])
            self.fontpreference.set_font_name(self.fontname)
            self.config.set("style","theme",active)
            self.colorpreference.set_color(gtk.gdk.color_parse(self.style['foreground']))
            self.bgpreference.set_color(gtk.gdk.color_parse(self.style['background']))
            self.borderpreference.set_color(gtk.gdk.color_parse(self.style['border']))
            self.paddingpreference.set_value(self.style['padding'])
            self.widthpreference.set_value(self.style['size'][0])
            self.heightpreference.set_value(self.style['size'][1])
            self.graphical.status.set_text(_('Style Changed to %s' % (active)))
            self.presetscombobox.set_active(activeid)
    	
    def show(self):
		self.dlg = self.wTree.get_widget("dialog-preferences")
		self.dlg.show()
		
    def togglelines(self, widget):
        b = not self.graphical.textbox.get_show_line_numbers()
        self.graphical.textbox.set_show_line_numbers(b)        

    def QuitEvent(self, widget, data=None):
    	print "Exiting..."
    	gtk.main_quit()
    	return False

    def kill_preferences(self, widget, data=None):
        self.dlg.hide()
