import urwid

from mitzasql.ui.widgets.base_db_view import BaseDBView
from mitzasql.ui.widgets.table import Table

from mitzasql.ui.widgets.cmd_proc import (BaseCmdProcessor, SearchCmdProcessor)

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
    def __init__(self, model, connection):
        self._command_processor = CommandProcessor(self)
        self._table_widget_cls = Table
        super().__init__(model, connection)
        self._command_processor.cmd_args_suggestions['resize'] = [c['name'] for c in self._model.columns]
        if connection.database is None:
            database = ''
        else:
            database = connection.database

    def refresh(self, query, connection):
        if query == self._model.query:
            return

        self._model.query = query
        self._model.reload()
        self._query_editor.query = query
        self._update_breadcrumbs()

    def resize_tbl_col(self, column, value=1):
        try:
            value = int(value)
            col_index = self._model.col_index(column.lower())
        except ValueError as e:
            # TODO: show column not found, or invalid col size
            return
        self._table.resize_col(col_index, value)
