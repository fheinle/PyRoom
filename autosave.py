# -*- coding: utf-8 -*-

"""
    PyRoom - A clone of WriteRoom
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    automatic saving

    :copyright: 2007 Nicolas P. Rougier & NoWhereMan Copyright
    :copyright: 2008 The PyRoom Theme - See AUTHORS file for more information
    :license: GNU General Public License, version 3 or later
"""

import gobject
import os
import tempfile
from pyroom_error import PyroomError


ELAPSED_TIME = 0 # elapsed time in seconds
AUTOSAVE_TIME = 3 # the timeout time in minutes
TEMP_FOLDER = "/var/tmp/pyroom"
TIMEOUT_ID = 0

FILE_UNNAMED = _('* Unnamed *')  ##repeted definition delete if possible


def autosave_init(edit_instance, mill=1000):
    """Init the internal autosave timer"""
    global ELAPSED_TIME
    global TIMEOUT_ID
    TIMEOUT_ID = gobject.timeout_add(mill, timeout, edit_instance)
    ELAPSED_TIME = 0  ## init the ELAPSED_TIME_var


def save_file(filename, text):
    """save text fo filename"""
    try:
        out_file = open(filename, "w")
        out_file.write(text)
        out_file.close()
    except IOError:
        raise PyroomError(_("Could not autosave file %s") % filename)

def autosave_quit():
    """dispose the internal timer"""
    gobject.source_remove(TIMEOUT_ID)


def autosave_file(edit_instance, buf_id):
    """AutoSave the Buffer to temp folder"""
    buf = edit_instance.buffers[buf_id]
    if not os.path.exists(TEMP_FOLDER):
        os.mkdir(TEMP_FOLDER)

    try:
        buf.tmp_filename
    except AttributeError:
        if buf.filename == FILE_UNNAMED:
            buf.tmp_filename = tempfile.mkstemp(suffix="",
                prefix="noname_"+"tmp_", dir=TEMP_FOLDER, text=True)[1]
        else:
            buf_name = os.path.split(buf.filename)[1]
            buf.tmp_filename = tempfile.mkstemp(suffix="",
                prefix = buf_name + "_tmp_", dir=TEMP_FOLDER, text=True)[1]
    save_file(buf.tmp_filename, buf.get_text(buf.get_start_iter(),
        buf.get_end_iter()))
    # Inform the user of the saving operation
    edit_instance.status.set_text(_('AutoSaving Buffer %(buf_id)d, to temp\
     file %(buf_tmp_filename)s') % {'buf_id': buf_id, 
                   'buf_tmp_filename': buf.tmp_filename})


def timeout(edit_instance):
    "the Timer Function"
    global ELAPSED_TIME
    global AUTOSAVE_TIME

    if int(AUTOSAVE_TIME) != 0:
        ELAPSED_TIME += 1
        if ELAPSED_TIME >= int(AUTOSAVE_TIME) * 60:
            for buf in edit_instance.buffers:
                autosave_file(edit_instance, 
                    edit_instance.buffers.index(buf))
            ELAPSED_TIME = 0
        return True # continue repeat timeout event
    else:
        return False #stop timeout event



