import gtk
import gtk.glade
import styles

# this will be changed when styles are stored in external files
styleslist = ['green','darkgreen','blue','c64','locontrast','cupid','banker']

class Preferences():
    def __init__(self,gui,style,verbose, ret):
        self.wTree = gtk.glade.XML("preferences.glade", "dialog-preferences")
        self.window = self.wTree.get_widget("dialog-preferences")
        self.fontpreference = self.wTree.get_widget("fontbutton")
        self.colorpreference = self.wTree.get_widget("colorbutton")
        self.bgpreference = self.wTree.get_widget("bgbutton")
        self.borderpreference = self.wTree.get_widget("borderbutton")
        self.presetscombobox = self.wTree.get_widget("presetscombobox")
        self.linenumbers = self.wTree.get_widget("linescheck")
        self.graphical = gui
        self.window.set_transient_for(self.graphical.window)

        for i in styleslist:
            self.presetscombobox.append_text(i)
        self.presetscombobox.set_active(0)

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

    def getcustomdata(self):
        self.fontname = self.fontpreference.get_font_name()
        self.fontsize = int(self.fontname[-2:])
        self.colorname = gtk.gdk.Color.to_string(self.colorpreference.get_color())
        self.bgname = gtk.gdk.Color.to_string(self.bgpreference.get_color())
        self.bordername = gtk.gdk.Color.to_string(self.borderpreference.get_color())

    def set_preferences(self, widget, data=None):

        self.preset = self.presetscombobox.get_active_text()
        self.dlg.hide()

    def customchanged(self, widget):
        self.presetscombobox.set_active(0)
        self.presetchanged()

    def presetchanged(self, widget):
        active = self.presetscombobox.get_active_text()
        if active == 'Custom':
            getcustomdata()
        #here i will format the custom dictionary and apply_style it, once we have the conf thing working, it writes to the ~/.pyroom/custom.css
        else:
            self.graphical.apply_style(styles.styles[active])
            self.graphical.apply_style(styles.styles[active])
    	
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
