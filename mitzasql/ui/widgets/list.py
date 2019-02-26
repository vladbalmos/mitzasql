import urwid

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

    def keypress(self, size, key):
        if key == 'enter':
            urwid.emit_signal(self, self.SIGNAL_SELECTED, self, self.focus.item_value)
            return
        # vim style navigation
        if key == 'j' or key == 'J':
            key = 'down'
        if key == 'k' or key == 'K':
            key = 'up'
        return super().keypress(size, key)
