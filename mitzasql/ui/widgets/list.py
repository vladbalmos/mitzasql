# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .. import utils

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
