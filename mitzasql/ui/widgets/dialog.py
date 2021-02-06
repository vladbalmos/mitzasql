# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .action_bar_pile_container import ActionBarPileContainer

class Dialog(ActionBarPileContainer):
    SIGNAL_OK = 'ok'

    def __init__(self, message, actions=None, title='', height=5):
        if isinstance(message, str):
            message = urwid.Text(message, align='center')
        if actions is None:
            actions = [
                ('k', 'Ok', self.SIGNAL_OK)
                ]
        super().__init__(message, actions, height, line_box=True, line_box_title=title)
