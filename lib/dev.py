#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs
import sys
import os
import pprint
import inspect
import json

from os.path import join, basename, dirname

# 3rd Party Libs
import zencoding

import zencoding.actions
# Make sure to import this module as the __actions dict inside
# zencoding.__init__ does not become full as actions is not imported

##################################### TODO #####################################
"""
Create a list of zencoding actions first in dict format, and then exporting to
JSON as keybindings

"""
def enumerate_actions():
    actions = [] #

    for action_name, action_func in sorted(zencoding.__actions.items()):
        action = {
            "keys"    : ["TODO"],
            "command" : "run_zen_action",

            "args"    : {
                "action" : None
            }
        }

        args = action['args']
        args['action'] = action_name

        spec = inspect.getargspec(action_func)
        defaults = spec.defaults

        action_args = spec.args[1:]
        action_args_map = dict.fromkeys(action_args, 'ARG_TODO')

        if defaults:
            action_args_map.update (
                dict(zip(spec.args[-len(spec.defaults):], spec.defaults))
            )

        args.update(action_args_map)

        doc = inspect.getdoc(action_func)
        if doc: action['doc'] = doc# doc.split('@')[0].strip()
        actions.append(action)

    print json.dumps(actions, indent=2)
    # print pprint.pformat(actions)

def scratch():
    def do(a, b, c=5, d=5, *args, **kw):
        pass

    spec = inspect.getargspec(do)
    print inspect.formatargspec(spec)
    print inspect.getsourcelines(do)

    do(**{'a':5, 'b':8, 'c':9})

def test_css_expansion():
    from zencoding import utils
    from zencoding.zen_settings import zen_settings

    print zencoding.expand_abbreviation('d:n+bgd', 'css','xml')

if __name__ == '__main__':
    test_css_expansion()
################################################################################