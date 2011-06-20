#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs
import sys
import os
import pprint
import re

import sublime

from os.path import join
from itertools import chain
from collections import defaultdict
from functools import wraps

################################## ZEN IMPORTS #################################

# Some may not be needed, and maybe not any at all, but in version 0.6 of Zen
# there were some runtime imports, so get these all in sys.modules now before
# the current directory '.' changes. Saves having to put an absolute path in
# `sys.path`

import zencoding
import zencoding.actions
import zencoding.actions.basic
import zencoding.actions.token
import zencoding.actions.traverse
import zencoding.filters
import zencoding.html_matcher
import zencoding.interface
import zencoding.interface.editor
import zencoding.interface.file
import zencoding.parser
import zencoding.parser.abbreviation
import zencoding.parser.css
import zencoding.parser.utils
import zencoding.parser.xml
import zencoding.resources
import zencoding.utils
import zencoding.zen_settings

from zencoding.zen_settings import zen_settings
from zencoding.interface.editor import ZenEditor

################################### CONSTANTS ##################################

CSS_PROP = 'meta.property-name'
ENCODING = 'utf8' # TODO

##################################### INIT #####################################

editor = ZenEditor()

def decode(s):
    return s.decode(ENCODING, 'ignore')

def expand_abbr(abbr, syntax = None, selection=True):
    # TODO: possibly create as an editor function
    syntax = syntax or editor.get_syntax()
    profile_name = editor.get_profile_name()
    content = zencoding.expand_abbreviation(abbr, syntax, profile_name)
    return decode(editor.add_placeholders(content, selection=selection))

###################################### CSS #####################################

css_snippets = zen_settings['css']['snippets']
css_sorted = sorted(tuple(map(decode, i)) for i in css_snippets.items())

def css_property_values():
    expanded = {}
    property_values = defaultdict(dict)

    for k in [k for k in css_snippets if ':' in k]:
        prop, value =  k.split(':') # abbreviation

        if prop not in expanded:
            prop = expanded[prop] = css_snippets[prop].split(':')[0]
        else:
            prop = expanded[prop]

        property_values[prop][value] = ( css_snippets[k].split(':')[1].rstrip(';'))

    return property_values
# apply has been removed in 3.2
css_property_values = css_property_values()

############################### MULTI SELECTIONS ###############################

def selections_context(view):
    sels = list(view.sel())
    ctxt_key = '__ctxter__'

    def merge():
        view.sel().clear()
        for sel in view.get_regions(ctxt_key):
            view.sel().add(sel)

        view.erase_regions(ctxt_key)

    def contexter():
        for sel in reversed(sels):
            view.sel().clear()
            view.sel().add(sel)

            yield sel # and run user code
            view.add_regions ( ctxt_key,
                (view.get_regions(ctxt_key) + list(view.sel())) , '')

    return contexter(), merge

def multi_selectable(f):
    @wraps(f)
    def wrapper(self, edit, **args):
        contexter, merge = selections_context(self.view)
        f(self, self.view, contexter, args)
        merge()
    return wrapper

#################################### HELPERS ###################################

def track_back(view, p, cond):
    for p in xrange(p, view.line(p).begin(), -1):
        if not cond(view, p):
            p += 1
            break

    return p

def find_css_property(view):
    scoped = lambda v,p: v.match_selector(p, CSS_PROP)
    end    = track_back(view,view.sel()[0].begin(),lambda v,p: not scoped(v, p))
    start  = track_back(view, end-1, scoped)

    return view.substr(sublime.Region(start, end))