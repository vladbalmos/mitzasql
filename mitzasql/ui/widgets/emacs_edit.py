import urwid

from .emacs_keys_mixin import EmacsKeysMixin

class EmacsEdit(urwid.Edit, EmacsKeysMixin):
    def __init__(self, edit_text='', allow_tab=False, mask=None, caption='', multiline=False):
        urwid.Edit.__init__(self, edit_text=edit_text, caption=caption,
                multiline=multiline, allow_tab=allow_tab, mask=mask, wrap='clip')

    def keypress(self, size, key):
        key = EmacsKeysMixin.keypress(self, size, key)
        if key is None:
            return
        return urwid.Edit.keypress(self, size, key)
