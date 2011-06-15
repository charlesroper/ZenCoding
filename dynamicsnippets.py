#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Standard Libs
import re

# Sublime Libs
import sublime
import sublime_plugin

################################## BASE CLASS ##################################

class SnippetsAsYouTypeBase(sublime_plugin.TextCommand):
    history = {}

    def insert(self, abbr):
        view = self.view

        def inner_insert():
            snippet = self.create_snippet(abbr) or ''
            edit=view.begin_edit()
            view.run_command('insert_snippet', { 'contents': snippet })
            view.end_edit(edit)

        if not self.just_ran:
            self.erase()
            sublime.set_timeout(inner_insert, 0)
        else:
            inner_insert()
            self.just_ran = False

    def erase(self):
        # called by insert and as on_cancel
        sublime.set_timeout(lambda: self.view.run_command('undo'), 0)

    def run(self, edit, **args):

        self.just_ran = True

        # self.init(view, args)
        args = frozenset(args.items())

        last_entry    =  self.history.get(args, '')
        self.insert(last_entry)

        def done(abbr):
            self.history[args] = abbr

        self.view.window().show_input_panel (
            self.input_message, last_entry, done, self.insert, self.erase )

################################################################################