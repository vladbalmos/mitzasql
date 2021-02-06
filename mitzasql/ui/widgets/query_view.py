# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .base_db_view import BaseDBView
from .table import Table
from .cmd_proc import (BaseCmdProcessor, SearchCmdProcessor, CommandError)

class CommandProcessor(BaseCmdProcessor):
    def __init__(self, query_view):
        self._query_view = query_view
        BaseCmdProcessor.__init__(self)

        self._colon_cmds.extend([
                ('r', 'resize', self._resize_table)
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
        self._query_view.resize_tbl_col(column, value)

class QueryView(BaseDBView):
    SIGNAL_ACTION_SELECT_ROW = 'select_row'

    def __init__(self, model, connection):
        self._command_processor = CommandProcessor(self)
        self._table_widget_cls = Table
        super().__init__(model, connection)
        self._command_processor.cmd_args_suggestions['resize'] = [c['name'] for c in self._model.columns]
        if connection.database is None:
            database = ''
        else:
            database = connection.database
        self.SIGNALS.append(self.SIGNAL_ACTION_SELECT_ROW)
        self._connect_table_signals()

    def _connect_table_signals(self):
        urwid.connect_signal(self._table, self._table.SIGNAL_ROW_SELECTED,
                self.select_row)

    def _disconnect_table_signals(self):
        urwid.disconnect_signal(self._table, self._table.SIGNAL_ROW_SELECTED,
                self.select_row)

    def select_row(self, emitter, row):
        urwid.emit_signal(self, self.SIGNAL_ACTION_SELECT_ROW, self, row)

    def refresh(self, query, connection):
        if query == self._model.query:
            self._model.reload()
            return

        self._model.query = query
        self._model.reload()
        self._query_editor.query = query
        self._update_breadcrumbs()

    def resize_tbl_col(self, column, value=1):
        try:
            value = int(value)
            col_index = self._model.col_index(column.lower())
        except IndexError as e:
            raise CommandError(u'Column not found!')
        except ValueError as e:
            raise CommandError(u'Invalid column width!')
        self._table.resize_col(col_index, value)
