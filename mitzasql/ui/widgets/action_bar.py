# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

class ActionBar(urwid.Columns):
    """Column widget containing actions labels and associated keys

    It's a cheap clone of the Midnight Commander action status bar
    """

    def __init__(self, actions):
        self._actions = actions
        column_widgets = self._create_widgets()
        super().__init__(column_widgets, dividechars=1)

    def _create_widgets(self):
        widgets = []
        for action_key, label in self._actions:
            label_width = len(label) + 4
            label_markup = self._create_label_markup(action_key, label)
            text = urwid.Padding(urwid.Text(label_markup, align='center'), align='center',
                    width=label_width)
            text = urwid.AttrMap(text, 'action_bar:action')
            widgets.append((label_width, text))
        return widgets

    def _create_label_markup(self, action_key, label):
        key_pos = label.find(action_key)
        if key_pos == -1:
            return label

        label_first_part = label[:key_pos]
        label_middle_part = ('action_bar:action_key', action_key)
        label_last_part = label[key_pos + len(action_key):]

        return [label_first_part, label_middle_part, label_last_part]
