# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .dialog import Dialog

class ErrorDialog(Dialog):
    def __init__(self, exception, title=u'Error', prefix=None):
        message = []
        message.append('\n')
        if prefix is not None:
            message.append(('error_message', prefix))
            message.append('\n\n')
        message.append(('error_message', str(exception)))
        message = urwid.Text(message, align='center')
        super().__init__(message, title=title)

    def keypress(self, size, key):
        if key == 'enter' or key == 'esc':
            urwid.emit_signal(self, self.SIGNAL_OK, self, 'Ok')
            return

        return super().keypress(size, key)
