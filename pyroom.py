#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# PyRoom - A clone of WriteRoom
# Copyright (c) 2007 Nicolas P. Rougier & NoWhereMan
# Copyright (c) 2008 Bruno Bord
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------------------------
#
# Based on code posted on ubuntu forums by NoWhereMan (www.nowhereland.it)
#  (Ubuntu thread was "WriteRoom/Darkroom/?")
#
# ------------------------------------------------------------------------------

import traceback
import sys
import os.path
import gobject
import gtk
import pango
import gtksourceview
import gettext

gettext.install('pyroom', 'locale')

# Some styles

styles = {'darkgreen': {
    'name': 'darkgreen',
    'background': '#000000',
    'foreground': '#007700',
    'lines': '#001100',
    'border': '#001100',
    'info': '#007700',
    'font': 'Droid Sans Mono',
    'fontsize': 12,
    'padding': 6,
    'size': [0.6, 0.95],
    }, 'green': {
    'name': 'green',
    'background': '#000000',
    'foreground': '#00ff00',
    'lines': '#007700',
    'border': '#003300',
    'info': '#00ff00',
    'font': 'Droid Sans Mono',
    'fontsize': 12,
    'padding': 6,
    'size': [0.6, 0.95],
    }, 'blue': {
    'name': 'blue',
    'background': '#0000ff',
    'foreground': '#ffffff',
    'lines': '#5555ff',
    'border': '#3333ff',
    'info': '#ffffff',
    'font': 'Droid Sans Mono',
    'fontsize': 12,
    'padding': 6,
    'size': [0.6, 0.95],
    }}

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

pyroom.py [-style] file1 file2 ...
style can be either 'blue', 'green', 'darkgreen'


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
Control-Left: Switch to previous buffer
Control-Right: Switch to next buffer
Control-Plus: Increases font size
Control-Minus: Decreases font size

Warnings:
---------
No autosave.
No question whether to close a modified buffer or not
""")


class FadeLabel(gtk.Label):
    """ GTK Label with timed fade out effect """

    active_duration = 3000  # Fade start after this time
    fade_duration = 1500  # Fade duration

    def __init__(self, message='', active_color=None, inactive_color=None):
        gtk.Label.__init__(self, message)
        if not active_color:
            active_color = '#ffffff'
        self.active_color = active_color
        if not inactive_color:
            inactive_color = '#000000'
        self.inactive_color = inactive_color
        self.idle = 0

    def set_text(self, message, duration=None):
        if not duration:
            duration = self.active_duration
        self.modify_fg(gtk.STATE_NORMAL,
                       gtk.gdk.color_parse(self.active_color))
        gtk.Label.set_text(self, message)
        if self.idle:
            gobject.source_remove(self.idle)
        self.idle = gobject.timeout_add(duration, self.fade_start)

    def fade_start(self):
        self.fade_level = 1.0
        if self.idle:
            gobject.source_remove(self.idle)
        self.idle = gobject.timeout_add(25, self.fade_out)

    def fade_out(self):
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


class PyRoom:
    """ The PyRoom class"""

    buffers = []
    current = 0

    def __init__(self, style):

        self.style = style

        # Main window

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_name('PyRoom')
        self.window.fullscreen()
        self.window.connect('delete_event', self.delete_event)
        self.window.connect('destroy', self.destroy)

        self.textbox = gtksourceview.SourceView()
        self.new_buffer()
        self.textbox.connect('scroll-event', self.scroll_event)
        self.textbox.connect('key-press-event', self.key_press_event)
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

        # Status

        self.status = FadeLabel()
        self.hbox = gtk.HBox()
        self.hbox.set_spacing(12)
        self.hbox.pack_end(self.status, True, True, 0)
        self.vbox.pack_end(self.hbox, False, False, 0)
        self.status.set_alignment(0.0, 0.5)
        self.status.set_justify(gtk.JUSTIFY_LEFT)
        self.apply_style()
        self.window.show_all()
        self.status.set_text(
            _('Welcome to PyRoom 1.0, type Control-H for help'))

    def delete_event(self, widget, event, data=None):
        """ Quit """
        return False

    def destroy(self, widget, data=None):
        """ Quit """
        gtk.main_quit()

    def key_press_event(self, widget, event):
        """ key press event dispatcher """

        bindings = {
            gtk.keysyms.Left: self.prev_buffer,
            gtk.keysyms.Right: self.next_buffer,
            gtk.keysyms.h: self.show_help,
            gtk.keysyms.i: self.show_info,
            gtk.keysyms.l: self.toggle_lines,
            gtk.keysyms.n: self.new_buffer,
            gtk.keysyms.o: self.open_file,
            gtk.keysyms.q: self.quit,
            gtk.keysyms.s: self.save_file,
            gtk.keysyms.w: self.close_buffer,
            gtk.keysyms.y: self.redo,
            gtk.keysyms.z: self.undo,
            gtk.keysyms.plus: self.plus,
            gtk.keysyms.minus: self.minus,
            }
        if event.state & gtk.gdk.CONTROL_MASK:

            # Special case for Control-Shift-s

            if event.state & gtk.gdk.SHIFT_MASK:
                print event.keyval
            if event.state & gtk.gdk.SHIFT_MASK and event.keyval\
                 == gtk.keysyms.S:
                self.save_file_as()
                return True
            if bindings.has_key(event.keyval):
                bindings[event.keyval]()
                return True
        return False

    def scroll_event(self, widget, event):
        """\" Scroll event dispatcher """

        if event.direction == gtk.gdk.SCROLL_UP:
            self.scroll_up()
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            self.scroll_down()

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

    def apply_style(self, style=None):
        """ """

        if style:
            self.style = style
        self.window.modify_bg(gtk.STATE_NORMAL,
                              gtk.gdk.color_parse(self.style['background'
                              ]))
        self.textbox.modify_bg(gtk.STATE_NORMAL,
                               gtk.gdk.color_parse(self.style['background'
                               ]))
        self.textbox.modify_base(gtk.STATE_NORMAL,
                                 gtk.gdk.color_parse(self.style['background'
                                 ]))
        self.textbox.modify_text(gtk.STATE_NORMAL,
                                 gtk.gdk.color_parse(self.style['foreground'
                                 ]))
        self.textbox.modify_fg(gtk.STATE_NORMAL,
                               gtk.gdk.color_parse(self.style['lines']))
        self.status.active_color = self.style['foreground']
        self.status.inactive_color = self.style['background']
        self.boxout.modify_bg(gtk.STATE_NORMAL,
                              gtk.gdk.color_parse(self.style['border']))
        font_and_size = '%s %d' % (self.style['font'],
                                   self.style['fontsize'])
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
        self.fixed.move(self.vbox, int(((1 - self.style['size'][0]) * w)/ 2),
            int(((1 - self.style['size'][1]) * h) / 2))
        self.textbox.set_border_width(self.style['padding'])

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

    def quit(self):
        """ quit pyroom """

        gtk.main_quit()

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
                errortext = '''Unable to open %(filename)s.''' % {'filename': buffer.filename}
                if errno == 2:
                  errortext += ' The file does not exist.'
                elif errno == 13:
                  errortext += ' You do not have permission to open the file.'
                buffer.set_text(_(errortext))
                print ('''Unable to open %(filename)s. %(traceback)s'''
                  % {'filename': buffer.filename, 'traceback': traceback.format_exc()})
                self.status.set_text(_('Failed to open %s')
                         % buffer.filename)
                buffer.filename = FILE_UNNAMED
            except:
                buffer.set_text(_('Unable to open %s\n'
                                 % buffer.filename))
                print ('''Unable to open %(filename)s. %(traceback)s'''
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

    def plus(self):
        """ Increases the font size"""

        self.style['fontsize'] += 2
        self.apply_style()
        self.status.set_text(_('Font size increased'))

    def minus(self):
        """ Decreases the font size"""

        self.style['fontsize'] -= 2
        self.apply_style()
        self.status.set_text(_('Font size decreased'))


if __name__ == '__main__':
    style = 'green'
    files = []

    # Look for style and file on command line
    for arg in sys.argv[1:]:
        if arg[0] == '-':
            t = arg[1:]
            if styles.has_key(arg[1:]):
                style = arg[1:]
        else:
            files.append(arg)

    # Create relevant buffers for file and load them
    pyroom = PyRoom(styles[style])
    if len(files):
        for filename in files:
            buffer = pyroom.new_buffer()
            buffer.filename = filename
            if os.path.exists(filename):
                try:
                    print filename
                    f = open(filename, 'r')
                    buffer.begin_not_undoable_action()
                    buffer.set_text(unicode(f.read(), 'utf-8'))
                    buffer.end_not_undoable_action()
                    f.close()
                except IOError, (errno, strerror):
                    errortext = '''Unable to open %(filename)s.''' % {'filename': buffer.filename}
                    if errno == 13:
                        errortext += ' You do not have permission to open the file.'
                    buffer.set_text(_(errortext))
                    print ('''Unable to open %(filename)s. %(traceback)s'''
                                     % {'filename': buffer.filename,
                                    'traceback': traceback.format_exc()})
                    buffer.filename = FILE_UNNAMED
                except:
                    buffer.set_text(_('Unable to open %s\n'
                                     % buffer.filename))
                    print ('''Unable to open %(filename)s. %(traceback)s'''
                                     % {'filename': buffer.filename,
                                    'traceback': traceback.format_exc()})
                    buffer.filename = FILE_UNNAMED

        pyroom.set_buffer(0)
        pyroom.close_buffer()
    gtk.main()

# EOF
