#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs
import os
import sys
import re
import random
import time

import logging

# Sublime Libs
import sublime
import sublime_plugin

# Zen Coding libs
from zencoding.parser.abbreviation import ZenInvalidAbbreviation

# Dynamic Snippet Base Class
from dynamicsnippets import SnippetsAsYouTypeBase

import zencoding
import zencoding.actions

from sublimezen import ( css_snippets, decode, expand_abbr, editor, css_sorted,
                         css_property_values, multi_selectable, CSS_PROP,
                         find_css_property, find_tag_start, find_tag_name,
                         find_attribute_name, css_prefixer )

from zenmeta    import ( CSS_PROP_VALUES, HTML_ELEMENTS_ATTRIBUTES,
                         HTML_ATTRIBUTES_VALUES )

from zencoding.html_matcher import last_match

################################### CONSTANTS ##################################

HTML                      = "text.html - source"

HTML_INSIDE_TAG_ANYWHERE  = "text.html meta.tag"
HTML_INSIDE_TAG           = "text.html meta.tag - string"
HTML_INSIDE_TAG_ATTRIBUTE = "text.html meta.tag string"

HTML_NOT_INSIDE_TAG       = 'text.html - meta.tag'

CSS          = 'source.css'
CSS_PROPERTY = 'source.css meta.property-list.css - meta.property-value.css'

CSS_PROPERTY_NAME =  u'source.css meta.property-list.css meta.property-name.css'

CSS_PREFIXER = 'source.css meta.property-list.css, meta.selector.css'
CSS_VALUE    = 'source.css meta.property-list.css meta.property-value.css'

CSS_ENTITY_SELECTOR = 'source.css meta.selector.css entity.other.attribute-name'

#################################### AUTHORS ###################################

__version__     = '1.5.0a'

__zen_version__ = '0.7'

__authors__     = ['"Sergey Chikuyonok" <serge.che@gmail.com>'
                   '"Вадим Макеев"      <pepelsbey@gmail.com>',
                   '"Nicholas Dudfield" <ndudfield@gmail.com>']

#################################### LOGGING ###################################

DEBUG_LEVEL  = 10

# TODO: why the fuck doesn't this work
zen_logger   = logging.getLogger('ZenLogger')
debug        = zen_logger.debug

zen_logger.setLevel(DEBUG_LEVEL)

def debug(f):
    if DEBUG_LEVEL: print 'ZenCoding:', f

def oq_debug(f):
    debug("on_query_completions %s" % f)

########################## DYNAMIC ZEN CODING SNIPPETS #########################

class ZenAsYouType(SnippetsAsYouTypeBase):
    input_message = "Enter Koan: "

    def create_snippet(self, abbr):
        try:
            return expand_abbr(abbr)
        except ZenInvalidAbbreviation:
            "dont litter the console"

class RunZenAction(sublime_plugin.TextCommand):
    @multi_selectable
    def run(self, view, contexter, kw):

        for i, selection in enumerate(contexter):
            args = kw.copy()

            action = args.pop('action')
            zencoding.run_action(action, editor, **args)
            
            # if action.startswith('match_pair'):
            #     last_match['opening_tag'] = None
            #     last_match['closing_tag'] = None
            #     last_match['start_ix']    = -1
            #     last_match['end_ix']      = -1

class SetHtmlSyntaxAndInsertSkel(sublime_plugin.TextCommand):
    def run(self, edit, doctype=None):
        view     = self.view

        settings = {} # TODO sublime.load_settings ? keymap args?
        syntax   = settings.get('default_html_syntax',
                                'Packages/HTML/HTML.tmlanguage')

        view.set_syntax_file(syntax)
        view.run_command( 'insert_snippet',
                          {'contents': expand_abbr('html:%s' % doctype)} )

class ZenCssMnemonic(sublime_plugin.WindowCommand):
    " Insert css snippets from QuickPanel"

    def is_enabled(self, **args):
        return len(self.window.active_view().sel()) == 1

    def run(self, prop_value=False):
        window = self.window
        view = window.active_view()

        if prop_value:
            pos      = view.sel()[0].b
            prop     = find_css_property(window.active_view(), pos)
            forpanel = sorted((css_property_values.get(prop) or {}).items())
            contents = lambda i: forpanel[i][1]
            # TODO expand while selector matches
            "meta.property-value.css - punctuation"
            # Then insert snippet over top of selection
        else:
            forpanel = css_sorted
            contents = lambda i: expand_abbr(forpanel[i][0])

        def done(i):
            if i != -1:
                view.run_command('insert_snippet', {'contents': contents(i)})

        display  = [list(reversed(i)) for i in forpanel]
        window.show_quick_panel(display, done)

class ZenListener(sublime_plugin.EventListener):
    def correct_syntax(self, view):
        return view.match_selector( view.sel()[0].b,
                                    'text.html, text.xml, source.css' )

    def css_property_values(self, view, prefix, pos):
        prefix = css_prefixer(view, pos)
        prop   = find_css_property(view, pos)
        # These `values` are sourced from all the fully specified zen abbrevs
        # `d:n` => `display:none` so `display:n{tab}` will yield `none`
        values = css_property_values.get(prop)

        if values and prefix and prefix in values:
            oq_debug("zcprop:val prop: %r values: %r" % (prop, values))
            return [(prefix, d, d) for d,d in sorted(values.items())]
        else:
            # Look for values relating to that property
            # Remove exact matches, so a \t is inserted
            values =  [v for v in CSS_PROP_VALUES.get(prop, []) if v != prefix]
            if values:
                debug("zenmeta:val prop: %r values: %r" % (prop, values))
                return [(prefix, v, v) for v in values]

    def html_elements_attributes(self, view, prefix, pos):
        tag         = find_tag_name(view, pos)
        values      = HTML_ELEMENTS_ATTRIBUTES.get(tag, [])
        return [(v, '%s="$1" $2' % v) for v in values]

    def html_attributes_values(self, view, prefix, pos):
        attr        = find_attribute_name(view, pos)
        values      = HTML_ATTRIBUTES_VALUES.get(attr, [])
        return [(v, v) for v in values]

    def on_query_completions(self, view, prefix, locations):
        if not self.correct_syntax(view): return []

        # We need to use one function rather than discrete listeners so as to
        # avoid pollution with less specific completions. Try to return early
        # with the most specific match possible.

        oq_debug("prefix: %r" % prefix)

        # A mapping of scopes, sub scopes and handlers, first matching of which
        # is used.
        COMPLETIONS = (

            (CSS,  ( (CSS_VALUE,                 self.css_property_values), )),
            (HTML, ( (HTML_INSIDE_TAG,           self.html_elements_attributes),
                     (HTML_INSIDE_TAG_ATTRIBUTE, self.html_attributes_values) ))
        )

        pos = view.sel()[0].b

        # Try to find some more specific contextual abbreviation
        for root_selector, sub_selectors in COMPLETIONS:
            for sub_selector, handler in sub_selectors:
                if view.match_selector(pos,  sub_selector):

                    c = handler.__name__, prefix
                    oq_debug('handler: %r prefix: %r' % c)

                    completions = handler(view, prefix, pos)
                    oq_debug('completions: %r' % completions)
                    if completions: return completions

        # Expand Zen expressions such as `d:n+m:a` or `div*5`
        try:
            abbr = zencoding.actions.basic.find_abbreviation(editor)
            oq_debug('abbr: %r' % abbr)

            if abbr:
                result = expand_abbr(abbr)
                oq_debug('abbr: %r result: %r' % (abbr, result))
                return [(abbr, result if '<' not in result else abbr, result)]

        except ZenInvalidAbbreviation:
            pass

        # If it wasn't a valid Zen css snippet, or the prefix is empty ''
        # then get warm and fuzzy with css properties.

        # TODO, before or after this, fuzz directly against the zen snippets
        # eg  `tjd` matching `tj:d` to expand `text-justify:distribute;`

        if view.match_selector(pos, CSS_PROPERTY):
            # Use this to get non \w based prefixes
            prefix     = css_prefixer(view, pos)
            properties = sorted(CSS_PROP_VALUES.keys())
            exacts     = [p for p in properties if p.startswith(prefix)]

            if exacts: properties = exacts
            else:      properties = [ p for p in properties if
                                      # to allow for fuzzy, which will
                                      # generally start with first letter
                                      p.startswith(prefix[0].lower()) ]

            oq_debug('css_property prefix: %r properties: %r' % ( prefix,
                                                                  properties ))

            return sorted((prefix, v, '%s:$0;' %  v) for v in properties)
        else:
            return []

    @staticmethod
    def check_context(view):
        abbr        =       zencoding.actions.basic.find_abbreviation(editor)
        if abbr:
            try:            result = expand_abbr(abbr)
            except          ZenInvalidAbbreviation: return None
            if result:
                return result

    def on_query_context(self, view, key, op, operand, match_all):
        if key == 'is_zen':
            debug('checking iz_zen context')
            context = Context.check_context(view)

            if context is not None:
                debug('is_zen context enabled')
                return True
            else:
                debug('is_zen context disabled')
                return False

################################################################################