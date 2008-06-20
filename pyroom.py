#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyRoom - A clone of WriteRoom
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Based on code posted on ubuntu forums by NoWhereMan (www.nowhereland.it)
    (Ubuntu thread was "WriteRoom/Darkroom/?")

    :copyright: 2007 Nicolas P. Rougier & NoWhereMan Copyright
    :copyright: 2008 The PyRoom Theme - See AUthors file for more information
    :license: GNU General Public License, version 3 or later
"""

__VERSION__ = '0.2'

import gettext
gettext.install('pyroom', 'locale')
import locale
locale.setlocale(locale.LC_ALL, '')
from optparse import OptionParser
import traceback

import gtk

import autosave
from basic_edit import BasicEdit
from pyroom_error import PyroomError
from preferences import PyroomConfig

pyroom_config = PyroomConfig()

if __name__ == '__main__':

    verbose = False

    files = []
    style = pyroom_config.config.get('visual', 'theme')
    autosave.autosave_time = pyroom_config.config.get('editor', 'autosavetime')

    # Preparing the themes list for the optionparser
    themes_list = pyroom_config.read_themes_list()
    themes_list.append('custom')

    # Get commandline args
    parser = OptionParser(usage = _('%prog [-v] [--style={style name}] \
[file1] [file2]...'),
                        version = '%prog ' + __VERSION__,
                        description = _('PyRoom lets you edit text files \
simply and efficiently in a full-screen window, with no distractions.'))
    parser.set_defaults(verbose=False,
                        style=pyroom_config.config.get('visual', 'theme'),
                        autosave_time=pyroom_config.config.get('editor',
                                                        'autosavetime'))
    parser.add_option('-a', '--autosave',
                    type='int', action='store', dest='autosave_time',
                    help=_('Specify the amount of time, in minutes, to \
                              automatically save your work.'))
    parser.add_option('-v', '--verbose',
                    action='store_true', dest = 'verbose',
                    help=_('Turn on verbose mode.'))
    parser.add_option('-s', '--style',
                    action='store', dest='style',
                    type='choice', choices=themes_list,
                    help=_('Override the default style'))
    (options, args) = parser.parse_args()

    verbose = options.verbose
    style = options.style
    autosave.autosave_time = options.autosave_time
    files = args

    # Create relevant buffers for file and load them
    pyroom = BasicEdit(style=style, verbose=verbose,
             pyroom_config=pyroom_config)
    try:
        buffnum = 0
        if len(files):
            for filename in files:
                pyroom.open_file_no_chooser(filename)
                buffnum += 1

        pyroom.set_buffer(buffnum)

        pyroom.status.set_text(
            _('Welcome to Pyroom %s, type Control-H for help' % __VERSION__))
        gtk.main()
    except PyroomError, e:
        # To change the format of the error text, edit pyroom_error
        pyroom.gui.error.set_text(str(e))
        if verbose:
            print str(e)
            print e.traceback
    except:
        print traceback.format_exc()
