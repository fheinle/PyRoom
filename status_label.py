#!/usr/bin/env python
#Includes the class for status label.

import gobject
import gtk

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

# EOF
