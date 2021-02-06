# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .emacs_keys_mixin import EmacsKeysMixin

class EmacsEdit(urwid.Edit, EmacsKeysMixin):
    def __init__(self, edit_text='', allow_tab=False, mask=None, caption='',
            multiline=False, read_only=False, wrap='clip'):
        urwid.Edit.__init__(self, edit_text=edit_text, caption=caption,
                multiline=multiline, allow_tab=allow_tab, mask=mask, wrap=wrap)
        self.read_only = read_only

    def selectable(self):
        return not self.read_only

    def keypress(self, size, key):
        key = EmacsKeysMixin.keypress(self, size, key)
        if key is None:
            return

        return urwid.Edit.keypress(self, size, key)
