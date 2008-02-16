import gtk
import gtksourceview
def check_unsaved_buffer(self):
    buffer = self.buffers[self.current]
    if buffer.can_undo() or buffer.can_redo():
        dialog = gtk.MessageDialog(self.window,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_WARNING, gtk.BUTTONS_YES_NO, 
                    "You are about to close a buffer that has unsaved changes. Do you want to save them?")
        dialog.set_title("Save?")

        if dialog.run() == gtk.RESPONSE_NO: 
            ret = False
        else: 
            ret = True
        dialog.destroy() 
        if ret:
            if buffer.filename == FILE_UNNAMED:
                self.save_file_as()
            else:
                self.save_file()

        
def save_unsaved_on_exit(self):
    count = 0
    ret = False
    for buffer in self.buffers:
        if buffer.can_undo() or buffer.can_redo():
            count = count + 1
    if count > 0:
        dialog = gtk.MessageDialog(self.window,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_WARNING, gtk.BUTTONS_YES_NO, 
                    "You are about to exit leaving unsaved files. Do you want to save them?")
        dialog.set_title("Save?")
            
        if dialog.run() == gtk.RESPONSE_NO: 
            ret = False
        else: 
            ret = True
        dialog.destroy() 
    
    if ret:
        for buffer in self.buffers:  
            if buffer.can_undo() or buffer.can_redo():            
                    if buffer.filename == FILE_UNNAMED:
                        self.save_file_as()
                    else:
                        self.save_file()
