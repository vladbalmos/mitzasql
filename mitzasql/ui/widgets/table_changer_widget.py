# Copyright (c) 2019 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import urwid

from mitzasql.ui.widgets.emacs_edit import EmacsEdit
from mitzasql.ui.widgets.list import List

class TableChangerWidget(urwid.Frame):
    SIGNAL_ESCAPE = 'escape'
    SIGNAL_CHANGE_TABLE = 'change_table'

    def __init__(self, model):
        self._model = model;
        self._search_input = EmacsEdit()
        self._tables_list = self._create_tables_list()
        header = urwid.Pile([urwid.AttrMap(self._search_input, 'editbox'), urwid.Divider('-')])
        super().__init__(self._tables_list, header, focus_part='header')
        urwid.register_signal(self.__class__, [self.SIGNAL_ESCAPE, self.SIGNAL_CHANGE_TABLE])
        urwid.connect_signal(self._search_input, 'change', self.filter_list)
        urwid.connect_signal(self._tables_list,
                self._tables_list.SIGNAL_SELECTED, self.on_select_table)

    def on_select_table(self, emitter, value):
        urwid.emit_signal(self, self.SIGNAL_CHANGE_TABLE, self, value)

    def filter_list(self, emitter, value):
        self._tables_list.clear()
        for item in self._model:
            if not self._is_table(item):
                continue
            name = item[0]
            if not name.lower().startswith(value):
                continue
            self._tables_list.append(name)

    def keypress(self, size, key):
        if key == 'esc':
            urwid.emit_signal(self, self.SIGNAL_ESCAPE, self)
            return

        if key == 'tab':
            if self.focus_position == 'body':
                self.focus_position = 'header'
            else:
                self.focus_position = 'body'
            return

        if key == 'enter' and self.focus_position == 'header' and len(self._tables_list.body):
            self.focus_position = 'body'

        return super().keypress(size, key)

    def _is_table(self, row):
        type = row[-1]
        if type != 'BASE TABLE' and type != 'VIEW' and type != 'SYSTEM VIEW':
            return False
        return True

    def _create_tables_list(self):
        tables = []
        for item in self._model:
            if not self._is_table(item):
                continue
            tables.append(item[0])

        tables_list = List(tables)
        return tables_list

