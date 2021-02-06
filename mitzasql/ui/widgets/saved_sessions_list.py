# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .list import List
from .action_bar_pile_container import ActionBarPileContainer
from .action_bar import ActionBar

class SavedSessionsList(ActionBarPileContainer):
    # Signals handled by the select session UI screen
    SIGNAL_CONNECT = 'connect'
    SIGNAL_CREATE_NEW = 'new'
    SIGNAL_EDIT = 'edit'
    SIGNAL_DELETE = 'delete'
    SIGNAL_QUIT = 'quit'

    def __init__(self, sessions_list):
        list = List(sessions_list)
        self._list = list
        actions = [
                ('N', u'New', self.SIGNAL_CREATE_NEW),
                ('C', u'Connect', self.SIGNAL_CONNECT),
                ('E', u'Edit', self.SIGNAL_EDIT),
                ('D', u'Delete', self.SIGNAL_DELETE),
                ('Q', u'Quit', self.SIGNAL_QUIT),
                ]
        super().__init__(urwid.BoxAdapter(list, 10), actions, 10,
                line_box=True, line_box_title=u'Select Session')
        urwid.connect_signal(list, List.SIGNAL_SELECTED, self._emit_connect_signal)

    def _emit_connect_signal(self, emitter, *args, **kwargs):
        urwid.emit_signal(self, self.SIGNAL_CONNECT, self)

    def refresh(self, data):
        self._list.reset(data)

    @property
    def session(self):
        return self._list.focus.item_value


