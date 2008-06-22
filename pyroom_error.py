# -*- coding: utf-8 -*-

"""
    PyRoom - A clone of WriteRoom
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Our nice little exception

    :copyright: 2007 Nicolas P. Rougier & NoWhereMan Copyright
    :copyright: 2008 The PyRoom Theme - See AUTHORS file for more information
    :license: GNU General Public License, version 3 or later
"""

import traceback


class PyroomError (Exception):

    def __init__(self, message):
        self.value = 'ERROR: ' + message
        self.traceback = traceback.format_exc()

    def __str__(self):
        return repr(self.value)
