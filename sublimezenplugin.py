#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs
import os
import sys
import re
import random
import time

# Sublime Libs
import sublime
import sublime_plugin 

# Zen Coding libs

from zencoding.parser.abbreviation import ZenInvalidAbbreviation

# Dynamic Snippet Base Class
from dynamicsnippets import SnippetsAsYouTypeBase

# this 
from sublimezen import ( css_snippets, decode, expand_abbr, editor, css_sorted,
                         css_property_values, multi_selectable, track_back, 
                         find_css_property )

import zencoding
import zencoding.actions

################################### CONSTANTS ##################################

DEBUG    = 1 

#################################### AUTHORS ###################################

__version__  = '1.4.0a'

__authors__  = [ '"Sergey Chikuyonok" <serge.che@gmail.com>'
                 '"Вадим Макеев"      <pepelsbey@gmail.com>' ,
                 '"Nicholas Dudfield" <ndudfield@gmail.com>' ]

########################## DYNAMIC ZEN CODING SNIPPETS #########################

class ZenAsYouType(SnippetsAsYouTypeBase):
    input_message = "Enter Koan: "

    def create_snippet(self, abbr):
        return expand_abbr(abbr)

class RunZenAction(sublime_plugin.TextCommand):
    @multi_selectable
    def run(self, view, contexter, kw):
        for selection in contexter:
            args = kw.copy()
            zencoding.run_action(args.pop('action'), editor, **args)

class SetHtmlSyntaxAndInsertSkel(sublime_plugin.TextCommand):
    def run(self, edit, doctype=None):
        view = self.view
        settings = {} # TODO sublime.load_settings ? keymap args?
        
        syntax   = settings.get( 'default_html_syntax',
                                 'Packages/HTML/HTML.tmlanguage' )
        
        view.settings().set('syntax', syntax)
        view.run_command( 'insert_snippet', 
                          {"contents": expand_abbr('html:%s' % doctype)} )

class Context(sublime_plugin.EventListener):
    @staticmethod
    def check_context(view):
        abbr = zencoding.actions.basic.find_abbreviation(editor)
        
        if DEBUG: print 'zencontext found abbr', `abbr`

        if abbr:
            try: 
                result = expand_abbr(abbr)
            except ZenInvalidAbbreviation:
                return
            
            if DEBUG: print 'zencontext results', `result`

            if result:
                return result

    def on_query_context(self, view, key, op, operand, match_all):
        # sometimes None was getting passed
        view = view or sublime.active_window().active_view()

        if DEBUG: print 'on_query_context', key

        if key == 'is_zen':
            context = Context.check_context(view)
            if DEBUG: print 'checking context',

            if context is not None:
                if DEBUG: print 'zen context enabled'
                return True
            else:
                if DEBUG: print 'zen context disabled'
                return False

################################################################################