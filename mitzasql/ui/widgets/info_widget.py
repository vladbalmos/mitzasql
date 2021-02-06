# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .. import utils

class InfoWidget(urwid.ListBox):
    SIGNAL_ESCAPE = 'escape'
    SIGNAL_QUIT = 'quit'

    def __init__(self, contents):
        super().__init__(contents)
        urwid.register_signal(self.__class__, [self.SIGNAL_ESCAPE, self.SIGNAL_QUIT])

    def keypress(self, size, key):
        key = utils.vim2emacs_translation(key)
        if key == 'esc':
            urwid.emit_signal(self, self.SIGNAL_ESCAPE, self)
            return

        if key == 'f10':
            urwid.emit_signal(self, self.SIGNAL_QUIT, self)
            return

        return super().keypress(size, key)

