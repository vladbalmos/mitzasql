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

import mitzasql.ui.utils as utils

class List(urwid.ListBox):
    """Custom list which emits a `selected` signal if an item is selected"""

    SIGNAL_SELECTED = 'selected'
    def __init__(self, data):
        focus_list_walker = self._create_focus_list_walker(data)
        super().__init__(focus_list_walker)
        urwid.register_signal(self.__class__, [self.SIGNAL_SELECTED])

    def _create_focus_list_walker(self, data):
        selectables = []
        data.sort()
        for item in data:
            selectable = urwid.AttrMap(urwid.SelectableIcon(item, len(item) + 1),
                    'list:item:unfocused',
                    'list:item:focused')
            selectable.item_value = item
            selectables.append(selectable)
        return urwid.SimpleFocusListWalker(selectables)

    def reset(self, data):
        self.body.clear()
        self.body = self._create_focus_list_walker(data)

    def clear(self):
        self.body.clear()

    def append(self, item):
        selectable = urwid.AttrMap(urwid.SelectableIcon(item, len(item) + 1),
                'list:item:unfocused',
                'list:item:focused')
        selectable.item_value = item
        self.body.append(selectable)

    def keypress(self, size, key):
        key = utils.vim2emacs_translation(key)
        if key == 'enter' and self.focus is not None:
            urwid.emit_signal(self, self.SIGNAL_SELECTED, self, self.focus.item_value)
            return
        return super().keypress(size, key)
