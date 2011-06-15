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

# Dynamic Snippet Base Class
from dynamicsnippets import SnippetsAsYouTypeBase

# Zen Init
# This module sets the sys.path to enable importing of zencoding
from sublimezen import ( css_snippets, decode, expand_abbr, editor, css_sorted,
                         css_property_values, multi_selectable_zen, track_back, 
                         find_css_property )

# Zen Coding libs
import zencoding

################################### CONSTANTS ##################################

DEBUG    = 1 

#################################### AUTHORS ###################################

__version__  = '1.4.0a'

__authors__  = [ ' "Sergey Chikuyonok" <serge.che@gmail.com> '
                 ' "Вадим Макеев"      <pepelsbey@gmail.com> ',
                 ' "Nicholas Dudfield" <ndudfield@gmail.com> ' ]

########################## DYNAMIC ZEN CODING SNIPPETS #########################

class RunZenAction(sublime_plugin.TextCommand):
    @multi_selectable_zen
    def run(self, view, contexter, kw):
        for selection in contexter:
            args = kw.copy()
            zencoding.run_action(args.pop('action'), editor, **args)

class ZenAsYouType(SnippetsAsYouTypeBase):
    input_message = "Enter Koan: "

    def create_snippet(self, abbr):
        """
        :abbr:
            In a concrete sense, the on_change(line) from window.show_input_panel.

            eg.
                Enter Koan: ul>li*5

        :(doctype,):

            Destructuring the `args` of TextCommand.run(self, view, args)

            eg.

                With a binding as so:

                    <binding key="ctrl+alt+enter" command="zen_coding html">
                        <context name="selector" value="text.html"/>
                    </binding>

                doctype is html
        """

        return expand_abbr(abbr)

# class ExpandCSSValueAbbr(sublime_plugin.TextCommand):
#     @old_run
#     def run(self, view, (abbr, )):
#         prop = find_css_property(view)
#         values = css_property_values.get(prop)

#         view.run_command( 'insert_snippet',
#                          {'contents': values[abbr] if values and abbr in values
#                            else abbr + '\t'})

# class ZenCSSMnemonic(sublime_plugin.WindowCommand):
#     " Insert css snippets from QuickPanel"

#     def run(self, window, args):
#         if 'prop_value' in args:
#             prop = find_css_property(window.active_view())
#             forpanel = sorted((css_property_values.get(prop) or {}).items())
#             cmd = 'expand_c_s_s_value_abbr'
#         else:
#             forpanel = css_sorted
#             cmd = 'zen_expand_abbr'

#         display = [u'%-20s %s' % i for i in forpanel]
#         args    = [i[0] for i in forpanel]
#         window.show_quick_panel('', cmd, args, display)

# class ZenExpandAbbr(TabTriggeredBase):
#     " Used to expand sequential regex bindings etc"
#     def create_snippet(self, (abbr, )):
#         if DEBUG:
#             print 'ZenExpandAbbr', `abbr`

#         return expand_abbr(abbr)

# class SetHTMLSyntaxAndInsertSkel(sublime_plugin.TextCommand):
#     @old_run
#     def run(self, view, (skel, )):
#         if DEBUG:
#             print 'SetHTMLSyntaxAndInsertSkel', `skel`

#         syntax = sublime.options().get( 'default_html_syntax',
#                                         'Packages/HTML/HTML.tm_language' )
#         view.options().set('syntax', syntax)
#         view.run_command('zen_expand_abbr', {"0": 'html:%s' % skel})

class Context(sublime_plugin.EventListener):
    @staticmethod
    def check_context(view):
        abbr = zencoding.actions.basic.find_abbreviation(editor)
        if DEBUG: print 'zencontext found abbr', `abbr`

        if abbr:
            result = expand_abbr(abbr)
            if DEBUG: print 'zencontext results', `result`

            if result:
                return result

    def on_query_context(self, view, key, op, operand, match_all):
        if key == "is_zen":
            if Context.check_context(view):
                return True

        return False

    def on_query_context(self, view, key, op, operand, match_all):
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