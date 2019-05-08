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
from mitzasql.ui.widgets.table import Table

from mitzasql.ui.widgets.cmd_proc import (BaseCmdProcessor, SearchCmdProcessor,
        CommandError)

class CommandProcessor(BaseCmdProcessor, SearchCmdProcessor):
    def __init__(self, db_tables_view):
        self._db_tables_view = db_tables_view
        BaseCmdProcessor.__init__(self)
        SearchCmdProcessor.__init__(self, self._db_tables_view.search_tables)

        self._colon_cmds.extend([
                ('r', 'resize', self._resize_table)
                ])

        self._cmd_strings = {
                '/': self.search,
                ':': self.colon_handler
                }
        self._cmd_keys = {
                'n': self.search_next,
                'N': self.search_prev
                }

    def _resize_table(self, *args):
        if not len(args):
            return
        if len(args) == 1:
            column = args[0]
            value = 1
        else:
            column, *value = args
            value = ' '.join(value)
        try:
            self._db_tables_view.resize_tbl_col(column, value)
        except CommandError as e:
            self._emit_error(str(e))

class DBTablesView(BaseDBView):
    SIGNAL_ACTION_SELECT_TABLE = 'select_table'
    def __init__(self, model, connection):
        self._command_processor = CommandProcessor(self)
        self._table_widget_cls = Table
        super().__init__(model, connection)
        self._command_processor.cmd_args_suggestions['resize'] = [c['name'] for c in self._model.columns]
        self.SIGNALS.append(self.SIGNAL_ACTION_SELECT_TABLE)
        self._connect_table_signals()

    def refresh(self, database, connection):
        if database == self._model.database:
            return
        self._model.database = database
        self._model.reload()
        self._update_breadcrumbs()

    def __del__(self):
        self._disconnect_table_signals()
        super().__del__()

    def _connect_table_signals(self):
        urwid.connect_signal(self._table, self._table.SIGNAL_ROW_SELECTED,
                self.select_table)

    def _disconnect_table_signals(self):
        urwid.disconnect_signal(self._table, self._table.SIGNAL_ROW_SELECTED,
                self.select_table)

    def resize_tbl_col(self, column, value=1):
        try:
            value = int(value)
            col_index = self._model.col_index(column)
        except IndexError as e:
            raise CommandError(u'Column does not exist!')
        except ValueError as e:
            raise CommandError(u'Invalid column width!')
        self._table.resize_col(col_index, value)

    def select_table(self, emitter, row):
        urwid.emit_signal(self, self.SIGNAL_ACTION_SELECT_TABLE, self, row)

    def search_tables(self, table, pos=0, reverse=False):
        result = self._model.search(table, col_index=0, pos=pos, reverse=reverse)
        if result is None:
            return
        index, row = result
        self._table.focus_row(index)
        return (index, row)
