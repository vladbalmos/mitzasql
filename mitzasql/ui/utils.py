# Copyright (c) 2019 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import time
import urwid

last_key_press = None
pending_vim_command = None

def orig_w(widget):
    if isinstance(widget, urwid.AttrMap):
        return widget.original_widget
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
