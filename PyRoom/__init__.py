# -*- coding:utf-8 -*-

""" translation setup """

__VERSION__ = '0.4.2'
import locale
try :
    locale.setlocale(locale.LC_ALL, '')
except :
    locale.setlocale(locale.LC_ALL, 'C')

import gettext
import gtk

import os
from os.path import pardir, abspath, dirname, join

GETTEXT_DOMAIN = 'pyroom'
LOCALE_PATH = abspath(join(dirname(__file__), pardir, 'locales'))
if not os.path.isdir(LOCALE_PATH):
    LOCALE_PATH = '/usr/share/locale'

# setup translation
languages_used = []
lc, encoding = locale.getlocale()

if lc:
    languages_used = [lc]
lang_in_env = os.environ.get('LANGUAGE', None)
if lang_in_env:
    languages_used.extend(lang_in_env.split())

gettext.bindtextdomain(GETTEXT_DOMAIN, LOCALE_PATH)
gettext.textdomain(GETTEXT_DOMAIN)

translation = gettext.translation(GETTEXT_DOMAIN, LOCALE_PATH,
                                  languages=languages_used,
                                  fallback=True)
import __builtin__
__builtin__._ = translation.gettext
