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

from mitzasql.ui.widgets.base_db_view import BaseDBView
from mitzasql.ui.widgets.mysql_table import MysqlTable

from mitzasql.ui.widgets.cmd_proc import (BaseCmdProcessor, CommandError)

class CommandProcessor(BaseCmdProcessor):
    def __init__(self, table_view):
        self._table_view = table_view
        BaseCmdProcessor.__init__(self)

        self._colon_cmds.extend([
                ('r', 'resize', self._resize_table),
                ('s', 'sort', self._sort_table)
                ])

        self._cmd_strings = {
                ':': self.colon_handler
                }

    def _resize_table(self, *args):
        if not len(args):
            return
        if len(args) == 1:
            column = args[0]
            value = 1
        else:
            column, value = args
        try:
            self._table_view.resize_tbl_col(column, value)
        except CommandError as e:
            self._emit_error(str(e))


    def _sort_table(self, *args):
        if not len(args):
            return

        if len(args) == 1:
            column = args[0]
            direction = 'asc'
        else:
            column, direction = args
        try:
            self._table_view.sort(column, direction)
        except CommandError as e:
            self._emit_error(str(e))

class TableView(BaseDBView):
    SIGNAL_ACTION_SELECT_ROW = 'select_row'
    SIGNAL_ACTION_INFO = 'info'
    SIGNAL_ACTION_CHANGE_TABLE = 'change_table'

    def __init__(self, model, connection):
        self._command_processor = CommandProcessor(self)
        self._table_widget_cls = MysqlTable
        actions = [
                ('F3', u'F3 Info', self.SIGNAL_ACTION_INFO)
                ]
        super().__init__(model, connection, actions)
        self._command_processor.cmd_args_suggestions['resize'] = [c['name'] for c in self._model.columns]
        self._command_processor.cmd_args_suggestions['sort'] = self._command_processor.cmd_args_suggestions['resize']
        self.SIGNALS.extend([self.SIGNAL_ACTION_SELECT_ROW,
            self.SIGNAL_ACTION_INFO, self.SIGNAL_ACTION_CHANGE_TABLE])
        self._connect_table_signals()

    def refresh(self, table, connection):
        if table == self._model.table_name:
            return

        self._model.table_name = table
        self._model.reload()
        self._command_processor.cmd_args_suggestions['resize'] = [c['name'] for c in self._model.columns]
        self._command_processor.cmd_args_suggestions['sort'] = self._command_processor.cmd_args_suggestions['resize']
        self._update_breadcrumbs()

    def refresh_model(self, emitter, action):
        self._model.reload(reset_limit=False, reset_order=False)

    def __del__(self):
        self._disconnect_table_signals()
        super().__del__()

    def _connect_table_signals(self):
        urwid.connect_signal(self._table, self._table.SIGNAL_ROW_SELECTED,
                self.select_row)

    def _disconnect_table_signals(self):
        urwid.disconnect_signal(self._table, self._table.SIGNAL_ROW_SELECTED,
                self.select_row)

    def select_row(self, emitter, row):
        urwid.emit_signal(self, self.SIGNAL_ACTION_SELECT_ROW, self, row)

    @property
    def table(self):
        return self._model.table_name

    def resize_tbl_col(self, column, value=1):
        try:
            value = int(value)
            col_index = self._model.col_index(column.lower())
        except IndexError as e:
            raise CommandError(u'Column not found!')
        except ValueError as e:
            raise CommandError(u'Invalid column width!')
        self._table.resize_col(col_index, value)

    def sort(self, column, direction):
        if column not in [c['name'] for c in self._model.columns]:
            raise CommandError(u'Column not found!')

        if direction.lower() != 'asc' and direction.lower() != 'desc':
            raise CommandError(u'Invalid sort direction!')

        self._model.sort(column, direction)

    def keypress(self, size, key):
        if key == 'ctrl p' and not self._focus_is('editor'):
            urwid.emit_signal(self, self.SIGNAL_ACTION_CHANGE_TABLE, self)
            return
        return super().keypress(size, key)
