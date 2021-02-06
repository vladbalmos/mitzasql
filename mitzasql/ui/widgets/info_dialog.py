# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .dialog import Dialog

class InfoDialog(Dialog):
    def __init__(self, info_message, title=u'Info'):
        message = []
        message.append('\n')
        message.append(info_message)
        message = urwid.Text(message, align='center')
        super().__init__(message, title=title)

    def keypress(self, size, key):
        if key == 'enter' or key == 'esc':
            urwid.emit_signal(self, self.SIGNAL_OK, self, 'Ok')
            return

        return super().keypress(size, key)
