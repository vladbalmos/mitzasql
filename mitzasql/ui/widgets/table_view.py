import urwid

from mitzasql.ui.widgets.base_db_view import BaseDBView
from mitzasql.ui.widgets.mysql_table import MysqlTable

from mitzasql.ui.widgets.cmd_proc import (BaseCmdProcessor)

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
        self._table_view.resize_tbl_col(column, value)

    def _sort_table(self, *args):
        if not len(args):
            return

        if len(args) == 1:
            column = args[0]
            direction = 'asc'
        else:
            column, direction = args
        self._table_view.sort(column, direction)

class TableView(BaseDBView):
    def __init__(self, model, connection):
        self._command_processor = CommandProcessor(self)
        self._table_widget_cls = MysqlTable
        super().__init__(model, connection)
        self._command_processor.cmd_args_suggestions['resize'] = [c['name'] for c in self._model.columns]
        self._command_processor.cmd_args_suggestions['sort'] = self._command_processor.cmd_args_suggestions['resize']
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
        pass

    def _disconnect_table_signals(self):
        pass

    @property
    def table(self):
        return self._model.table_name

    def resize_tbl_col(self, column, value=1):
        try:
            value = int(value)
            col_index = self._model.col_index(column.lower())
        except ValueError as e:
            # TODO: show column not found, or invalid col size
            return
        self._table.resize_col(col_index, value)

    def sort(self, column, direction):
        if column not in [c['name'] for c in self._model.columns]:
            # TODO: show column not found
            return

        if direction.lower() != 'asc' and direction.lower() != 'desc':
            # TODO: show invalid sort dir
            return
        self._model.sort(column, direction)

