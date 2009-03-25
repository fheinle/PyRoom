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
provide autosave functions
"""
import gobject
from pyroom_error import PyroomError
import os

def start_autosave(edit_instance):
    """start the autosave timer"""
    timeout_id = gobject.timeout_add(1000, autosave_timeout, edit_instance)
    edit_instance.autosave_timeout_id = timeout_id
    edit_instance.autosave_elapsed = 0

def stop_autosave(edit_instance):
    """stop the autosave timer and remove backup files"""
    for buf in edit_instance.buffers:
        autosave_fn = get_autosave_filename(buf.filename)
        if not buf.filename == edit_instance.UNNAMED_FILENAME and \
           os.path.isfile(autosave_fn):
            os.remove(autosave_fn)
    gobject.source_remove(edit_instance.autosave_timeout_id)

def autosave_timeout(edit_instance):
    """see if we have to autosave open files"""
    if edit_instance.preferences.autosave_time:
        if edit_instance.autosave_elapsed >= \
           edit_instance.preferences.autosave_time * 60:
            autosave(edit_instance)
            edit_instance.autosave_elapsed = 0
        else:
            edit_instance.autosave_elapsed += 1
    return True

def get_autosave_filename(filename):
    """get the filename autosave would happen to"""
    SUFFIX = ".pyroom-autosave"
    autosave_filename = os.path.join(
        os.path.dirname(filename),
        ".%s%s" % (os.path.basename(filename), SUFFIX)
    )
    return autosave_filename

def autosave(edit_instance):
    """save all open files that have been saved before"""
    for buf in edit_instance.buffers:
        if not buf.filename == edit_instance.UNNAMED_FILENAME:
            backup_file = open(
                get_autosave_filename(buf.filename),
                'w'
            )
            try:
                try:
                    backup_file.write(
                        buf.get_text(buf.get_start_iter(), buf.get_end_iter())
                    )
                except IOError:
                    raise PyroomError(_("Could not autosave file %s") % 
                                        filename)
            finally:
                backup_file.close()
