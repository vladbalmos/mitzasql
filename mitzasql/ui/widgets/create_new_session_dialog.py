# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .dialog import Dialog

class CreateNewSessionDialog(Dialog):
    SIGNAL_YES = 'Yes'
    SIGNAL_QUIT = 'Quit'

    def __init__(self):
        message = urwid.Text(u'No sessions defined. Do you want to create one?',
                align='center')
        actions = [
            ('Y', self.SIGNAL_YES, self.SIGNAL_YES),
            ('Q', self.SIGNAL_QUIT, self.SIGNAL_QUIT)
            ]

        super().__init__(message, actions)
