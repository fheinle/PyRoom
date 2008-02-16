import gtk
import gtksourceview

from status_label import FadeLabel
from gui import GUI

import restore_session #Allows a session to be restored with "-s"
import check_unsaved #Checks that a buffer is unmodified before closing


FILE_UNNAMED = _('* Unnamed *')

HELP = \
    _("""PyRoom - an adaptation of write room
Copyright (c) 2007 Nicolas Rougier, NoWhereMan
Copyright (c) 2008 Bruno Bord

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

Usage:
------

Usage: pyroom [-v] [--style={style name}] file1 file2
style can be either 'blue', 'green', 'darkgreen', 'banker', 'cupid'
                    'locontrast', 'c64'


Commands:
---------
Control-H: Show help in a new buffer
Control-I: Show buffer information
Control-L: Toggle line number
Control-N: Create a new buffer
Control-O: Open a file in a new buffer
Control-Q: Quit
Control-S: Save current buffer
Control-Shift-S: Save current buffer as
Control-W: Close buffer and exit if it was the last buffer
Control-Y: Redo last typing
Control-Z: Undo last typing
Control-Page Up: Switch to previous buffer
Control-Page Down: Switch to next buffer
Control-Plus: Increases font size
Control-Minus: Decreases font size

Warnings:
---------
No autosave.
No question whether to close a modified buffer or not
""")

class BasicEdit():
    def __init__(self,style,verbose, ret):
        self.ret = ret
        self.style = style
        self.gui = GUI(style)
        self.status = self.gui.status
        self.window = self.gui.window
        self.textbox = self.gui.textbox


        self.new_buffer()
        restore_session.open_session(self, ret)
        self.textbox.connect('key-press-event', self.key_press_event)
        self.status.set_text(
            _('Welcome to PyRoom 1.0, type Control-H for help'))
        self.window.show_all()
        self.window.fullscreen()
    def key_press_event(self, widget, event):
        """ key press event dispatcher """

        bindings = {
            gtk.keysyms.Page_Up: self.prev_buffer,
            gtk.keysyms.Page_Down: self.next_buffer,
            gtk.keysyms.h: self.show_help,
            gtk.keysyms.H: self.show_help,
            gtk.keysyms.i: self.show_info,
            gtk.keysyms.I: self.show_info,
            gtk.keysyms.l: self.toggle_lines,
            gtk.keysyms.L: self.toggle_lines,
            gtk.keysyms.n: self.new_buffer,
            gtk.keysyms.N: self.new_buffer,
            gtk.keysyms.o: self.open_file,
            gtk.keysyms.O: self.open_file,
            gtk.keysyms.q: self.quit,
            gtk.keysyms.Q: self.quit,
            gtk.keysyms.s: self.save_file,
            gtk.keysyms.S: self.save_file,
            gtk.keysyms.w: self.close_buffer,
            gtk.keysyms.W: self.close_buffer,
            gtk.keysyms.y: self.redo,
            gtk.keysyms.Y: self.redo,
            gtk.keysyms.z: self.undo,
            gtk.keysyms.Z: self.undo,
            gtk.keysyms.plus: self.gui.plus,
            gtk.keysyms.equal: self.gui.plus,
            gtk.keysyms.minus: self.gui.minus,
            }
        if event.state & gtk.gdk.CONTROL_MASK:

            # Special case for Control-Shift-s

            if event.state & gtk.gdk.SHIFT_MASK:
                print event.keyval
            if event.state & gtk.gdk.SHIFT_MASK and event.keyval\
                 == gtk.keysyms.S:
                self.edit.save_file_as()
                return True
            if bindings.has_key(event.keyval):
                bindings[event.keyval]()
                return True
        return False


    current = 0
    buffers = []
    def show_info(self):
        """ Display buffer information on status label for 5 seconds """

        buffer = self.buffers[self.current]
        if buffer.can_undo() or buffer.can_redo():
            status = _(' (modified)')
        else:
            status = ''
        self.status.set_text(_('Buffer %(buffer_id)d: %(buffer_name)s%(status)s, %(char_count)d byte(s), %(word_count)d word(s), %(lines)d line(s)') % {
            'buffer_id': self.current + 1,
            'buffer_name': buffer.filename,
            'status': status,
            'char_count': buffer.get_char_count(),
            'word_count': self.word_count(buffer),
            'lines': buffer.get_line_count(),
            }, 5000)
    def undo(self):
        """ Undo last typing """

        buffer = self.textbox.get_buffer()
        if buffer.can_undo():
            buffer.undo()
        else:
            self.status.set_text(_('No more undo!'))

    def redo(self):
        """ Redo last typing """

        buffer = self.textbox.get_buffer()
        if buffer.can_redo():
            buffer.redo()
        else:
            self.status.set_text(_('No more redo!'))

    def toggle_lines(self):
        """ Toggle lines number """

        b = not self.textbox.get_show_line_numbers()
        self.textbox.set_show_line_numbers(b)

    def open_file(self):
        """ Open file """

        chooser = gtk.FileChooserDialog('PyRoom', self.window,
                gtk.FILE_CHOOSER_ACTION_OPEN,
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)

        res = chooser.run()
        if res == gtk.RESPONSE_OK:
            buffer = self.new_buffer()
            buffer.filename = chooser.get_filename()
            try:
                f = open(buffer.filename, 'r')
                buffer = self.buffers[self.current]
                buffer.begin_not_undoable_action()
                utf8 = unicode(f.read(), 'utf-8')
                buffer.set_text(utf8)
                buffer.end_not_undoable_action()
                f.close()
                self.status.set_text(_('File %s open')
                         % buffer.filename)
            except IOError, (errno, strerror):
                errortext = _('Unable to open %(filename)s.' % {'filename': buffer.filename})
                if errno == 2:
                    errortext += _(' The file does not exist.')
                elif errno == 13:
                    errortext += _(' You do not have permission to open the file.')
                buffer.set_text(_(errortext))
                if verbose:
                    print ('Unable to open %(filename)s. %(traceback)s'
                        % {'filename': buffer.filename, 'traceback': traceback.format_exc()})
                self.status.set_text(_('Failed to open %s')
                    % buffer.filename)
                buffer.filename = FILE_UNNAMED
            except:
                buffer.set_text(_('Unable to open %s\n'
                                 % buffer.filename))
                if verbose:
                    print ('Unable to open %(filename)s. %(traceback)s'
                        % {'filename': buffer.filename,
                        'traceback': traceback.format_exc()})
                buffer.filename = FILE_UNNAMED
        else:
            self.status.set_text(_('Closed, no files selected'))
        chooser.destroy()

    def save_file(self):
        """ Save file """

        buffer = self.buffers[self.current]
        if buffer.filename != FILE_UNNAMED:
            f = open(buffer.filename, 'w')
            txt = buffer.get_text(buffer.get_start_iter(),
                                  buffer.get_end_iter())
            f.write(txt)
            f.close()
            buffer.begin_not_undoable_action()
            buffer.end_not_undoable_action()
            self.status.set_text(_('File %s saved') % buffer.filename)
        else:
            self.save_file_as()

    def save_file_as(self):
        """ Save file as """

        buffer = self.buffers[self.current]
        chooser = gtk.FileChooserDialog('PyRoom', self.window,
                gtk.FILE_CHOOSER_ACTION_SAVE,
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        if buffer.filename != FILE_UNNAMED:
            chooser.set_filename(buffer.filename)
        res = chooser.run()
        if res == gtk.RESPONSE_OK:
            buffer.filename = chooser.get_filename()
            self.save_file()
        else:
            self.status.set_text(_('Closed, no files selected'))
        chooser.destroy()

    # BB



    def word_count(self, buffer):
        """ Word count in a text buffer """

        iter1 = buffer.get_start_iter()
        iter2 = iter1.copy()
        iter2.forward_word_end()
        count = 0
        while iter2.get_offset() != iter1.get_offset():
            count += 1
            iter1 = iter2.copy()
            iter2.forward_word_end()
        return count

    def show_help(self):
        """ Create a new buffer and inserts help """
        buffer = self.new_buffer()
        buffer.begin_not_undoable_action()
        buffer.set_text(HELP)
        buffer.end_not_undoable_action()

    def new_buffer(self):
        """ Create a new buffer """

        buffer = gtksourceview.SourceBuffer()
        buffer.set_check_brackets(False)
        buffer.set_highlight(False)
        buffer.filename = FILE_UNNAMED
        self.buffers.insert(self.current + 1, buffer)
        buffer.place_cursor(buffer.get_start_iter())
        self.next_buffer()
        return buffer

    def close_buffer(self):
        """ Close current buffer """
        check_unsaved.check_unsaved_buffer(self)
        if len(self.buffers) > 1:

            self.buffers.pop(self.current)
            self.current = min(len(self.buffers) - 1, self.current)
            self.set_buffer(self.current)
        else:
            quit()

    def set_buffer(self, index):
        """ Set current buffer """

        if index >= 0 and index < len(self.buffers):
            self.current = index
            buffer = self.buffers[index]
            self.textbox.set_buffer(buffer)
            if hasattr(self, 'status'):
                self.status.set_text(
                    _('Switching to buffer %(buffer_id)d (%(buffer_name)s)'
                    % {'buffer_id': self.current + 1, 'buffer_name'
                    : buffer.filename}))

    def next_buffer(self):
        """ Switch to next buffer """

        if self.current < len(self.buffers) - 1:
            self.current += 1
        else:
            self.current = 0
        self.set_buffer(self.current)

    def prev_buffer(self):
        """ Switch to prev buffer """

        if self.current > 0:
            self.current -= 1
        else:
            self.current = len(self.buffers) - 1
        self.set_buffer(self.current)

    def quit(self):
        #Add any functions that you want to take place here before pyRoom quits
        check_unsaved.save_unsaved_on_exit(self)
        restore_session.save_session(self)
        self.gui.quit()

# EOF
