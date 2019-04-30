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

import urwid

from .query_editor import QueryEditor

class QueryWidget(urwid.AttrMap):
    def __init__(self):
        editor = QueryEditor()
        container = urwid.Filler(urwid.AttrMap(editor, ''), valign='top')
        title = u'[F9: Run. Ctrl-F9: Clear. Esc: Close. Ctrl-P/Ctrl-N: Query history]'
        line_box = urwid.LineBox(container, title=title,
                title_align='right')

        super().__init__(line_box, 'linebox')

    @property
    def query(self):
        return self.base_widget.edit_text

    @query.setter
    def query(self, query):
        self.base_widget.edit_text = query

    def clear(self):
        self.base_widget.edit_text = ''

    def keypress(self, size, key):
        key = super().keypress(size, key)
        # Disable the up key. It interferes with the parent pile container
        if key == 'up':
            return None
        return key
