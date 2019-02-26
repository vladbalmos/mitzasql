import urwid

from .emacs_keys_mixin import EmacsKeysMixin

class EmacsIntEdit(urwid.IntEdit, EmacsKeysMixin):
    def __init__(self, default=None):
        urwid.IntEdit.__init__(self, default=default)

    def keypress(self, size, key):
        key = EmacsKeysMixin.keypress(self, size, key)
        if key is None:
            return
        return urwid.Edit.keypress(self, size, key)
