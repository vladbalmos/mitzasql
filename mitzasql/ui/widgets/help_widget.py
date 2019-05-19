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

import os
import urwid
import mitzasql.ui.utils as utils

class HelpWidget(urwid.ListBox):
    SIGNAL_ESCAPE = 'escape'

    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), 'help.txt')
        try:
            with open(path) as file:
                help = file.read()
        except:
            help = u'Error: Unable to open help file'
        contents = [urwid.AttrMap(urwid.Text(help), 'default'),
                # Empty line is required, or else the 'end' key won't work
                urwid.AttrMap(urwid.Text(''), 'default')]
        super().__init__(contents)
        urwid.register_signal(self.__class__, [self.SIGNAL_ESCAPE])

    @property
    def name(self):
        return u'Help'

    def keypress(self, size, key):
        key = utils.vim2emacs_translation(key)
        if key == 'esc':
            urwid.emit_signal(self, self.SIGNAL_ESCAPE, self)
            return

        return super().keypress(size, key)
