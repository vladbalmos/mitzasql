import urwid

from .emacs_edit import EmacsEdit

class QueryEditor(EmacsEdit):
    def __init__(self):
        super().__init__(multiline=True, allow_tab=True)
