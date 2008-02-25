import gtk
import gtk.glade
import os.path
from status_label import FadeLabel
import ConfigParser
from pyroom_error import PyroomError
import autosave

# Getting the theme files and cleaning up the list, i use custom first so that it always have the index 0 in the list
themeslist = []
rawthemeslist = os.listdir("themes/")
for i in rawthemeslist:
    if i[-5:] == 'theme' and i != 'custom.theme':
        i = i[:-6]
        themeslist.append(i)
    
class Preferences():
    def __init__(self,gui,style,verbose):
        self.style = style
        self.wTree = gtk.glade.XML("interface.glade", "dialog-preferences")
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
        self.autosave_spinbutton = self.wTree.get_widget("spinbutton2")
        self.spellcheck = self.wTree.get_widget("spellchecktext")
        self.graphical = gui
        self.config = ConfigParser.ConfigParser()
        self.customfile = ConfigParser.ConfigParser()
        self.customfile.read("themes/custom.theme")
        self.config.read("example.conf")
        self.activestyle = self.config.get("visual","theme")
        self.linesstate = self.config.get("visual","linenumber")
        self.autosavestate = self.config.get("editor","autosave") 
        #self.autosavetime = self.config.get("editor","autosavetime")
        self.autosavetime=autosave.autosave_time
        self.autosave_spinbutton.set_value(float(self.autosavetime))
        self.spellcheckstate = self.config.get("editor","spellcheck")
        self.linesstate = int(self.linesstate)
        self.autosavestate = int(self.autosavestate)
        self.spellcheckstate = int(self.spellcheckstate)
        self.verbose = verbose

        self.linenumbers.set_active(self.linesstate)
        self.autosave.set_active(self.autosavestate)
        self.spellcheck.set_active(self.spellcheckstate)
        self.window.set_transient_for(self.graphical.window)

        self.stylesvalues = { 'custom' : 0 }
        self.startingvalue = 1

        for i in themeslist:
            self.stylesvalues['%s' % (i)] = self.startingvalue
            self.startingvalue = self.startingvalue + 1
            i = i.capitalize()
            self.presetscombobox.append_text(i)
        self.presetscombobox.set_active(self.stylesvalues[self.activestyle])
        self.presetchanged(self.presetscombobox,'initial')

        # Connecting interface's signals
        dic = {
                "on_MainWindow_destroy" : self.QuitEvent,
                "on_button-ok_clicked" : self.set_preferences,
                "on_button-close_clicked" : self.kill_preferences,
                }
        self.wTree.signal_autoconnect(dic)
        self.linenumbers.connect('toggled', self.togglelines)
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
        self.getcustomdata()
        self.linenumberspref = self.linenumbers.get_active()
        self.autosavepref = self.autosave.get_active()
        self.spellcheckpref = self.spellcheck.get_active()

        if self.linenumberspref == True:
            self.linenumberspref = 1
        else:
            self.linenumberspref = 0
        if self.autosavepref == True:
            self.autosavepref = 1
        else:
            self.autosavepref = 0
        if self.spellcheckpref == True:
            self.spellcheckpref = 1
        else:
            self.spellcheckpref = 0
            
        self.config.set("visual","linenumber",self.linenumberspref)
        self.config.set("editor","autosave",self.autosavepref)
        autosave.autosave_time=self.autosave_spinbutton.get_value_as_int() ## apply the autosave time settings
        self.config.set("editor","autosavetime",autosave.autosave_time)
        #print autosave.autosave_time,self.autosave_spinbutton.get_value_as_int() ## Debug
        self.config.set("editor","spellcheck",self.spellcheckpref)        
        if self.presetscombobox.get_active_text().lower() == 'custom':
            c = open("themes/custom.theme", "w")
            self.customfile.set("theme","background",self.bgname)
            self.customfile.set("theme","foreground",self.colorname)
            self.customfile.set("theme","border",self.bordername)
            self.customfile.set("theme","font",self.fontname)
            self.customfile.set("theme","fontsize",self.fontsize)
            self.customfile.set("theme","padding",self.paddingname)
            self.customfile.set("theme","width",self.widthname)
            self.customfile.set("theme","height",self.heightname)
            self.customfile.write(c)
        self.dlg.hide()
        try:
            f = open("example.conf", "w")
            self.config.write(f)
        except:
            e = PyroomError(_("Could not save preferences file."))
            self.graphical.error.set_text(str(e))
            if self.verbose:
                print str(e)
                print e.traceback
            

    def customchanged(self, widget):
        self.presetscombobox.set_active(0)
        self.presetchanged(widget)

    def presetchanged(self, widget, mode=None):
        if mode == 'initial':
            self.graphical.apply_style(self.style,'normal')
            self.fontname = self.graphical.config.get("theme","font") + ' ' + self.graphical.config.get("theme","fontsize")
            self.fontpreference.set_font_name(self.fontname)
            self.colorpreference.set_color(gtk.gdk.color_parse(self.graphical.config.get("theme","foreground")))
            self.bgpreference.set_color(gtk.gdk.color_parse(self.graphical.config.get("theme","background")))
            self.borderpreference.set_color(gtk.gdk.color_parse(self.graphical.config.get("theme","border")))
            self.paddingpreference.set_value(float(self.graphical.config.get("theme","padding")))
            self.widthpreference.set_value(float(self.graphical.config.get("theme","width")))
            self.heightpreference.set_value(float(self.graphical.config.get("theme","height")))
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
                self.graphical.apply_style(customstyle['Custom'],'custom')
                self.graphical.apply_style(customstyle['Custom'],'custom')
                self.config.set("visual","theme",active)
                self.graphical.status.set_text(_('Style Changed to %s' % (active)))
            else:
                theme = theme = "./themes/" + active + ".theme"
                self.graphical.config.read(theme)
                self.graphical.apply_style()
                self.graphical.apply_style()
                self.fontname = self.graphical.config.get("theme","font") + ' ' + self.graphical.config.get("theme","fontsize")
                self.fontpreference.set_font_name(self.fontname)
                self.config.set("visual","theme",active)
                self.colorpreference.set_color(gtk.gdk.color_parse(self.graphical.config.get("theme","foreground")))
                self.bgpreference.set_color(gtk.gdk.color_parse(self.graphical.config.get("theme","background")))
                self.borderpreference.set_color(gtk.gdk.color_parse(self.graphical.config.get("theme","border")))
                self.paddingpreference.set_value(float(self.graphical.config.get("theme","padding")))
                self.widthpreference.set_value(float(self.graphical.config.get("theme","width")))
                self.heightpreference.set_value(float(self.graphical.config.get("theme","height")))
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
