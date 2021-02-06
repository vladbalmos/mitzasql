# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import time
import urwid

last_key_press = None
pending_vim_command = None

def orig_w(widget):
    if isinstance(widget, urwid.AttrMap):
        return widget.original_widget
    return widget

def orig_w_recursive(widget):
    if hasattr(widget, 'original_widget'):
        return orig_w_recursive(widget.original_widget)

    return widget

def vim2emacs_translation(key):
    global last_key_press
    global pending_vim_command

    if key == 'j' or key == 'J':
        return 'down'

    if key == 'k' or key == 'K':
        return 'up'

    if key == 'ctrl u':
        return 'page up'

    if key == 'ctrl d':
        return 'page down'

    if key == 'G':
        return 'end'

    if key == 'g' and not pending_vim_command:
        last_key_press = time.time()
        pending_vim_command = 'g'
        return None

    if key == 'g' and pending_vim_command:
        diff = time.time() - last_key_press
        last_key_press = None
        pending_vim_command = None

        if diff < 0.25:
            return 'home'

    return key
