# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .base_db_view import BaseDBView
from .table import Table
from .cmd_proc import (BaseCmdProcessor, SearchCmdProcessor)

class CommandProcessor(BaseCmdProcessor, SearchCmdProcessor):
    def __init__(self, dbview):
        self._dbview = dbview
        BaseCmdProcessor.__init__(self)
        SearchCmdProcessor.__init__(self, self._dbview.search_db)
        self._cmd_strings = {
                '/': self.search
                }
        self._cmd_keys = {
                'n': self.search_next,
                'N': self.search_prev
                }

class DBView(BaseDBView):
    SIGNAL_ACTION_SELECT_DB = 'select_db'
    SIGNAL_ACTION_PROCESS_LIST = 'process_list'

    def __init__(self, model, connection):
        self._command_processor = CommandProcessor(self)
        self._table_widget_cls = Table
        super().__init__(model, connection)
        self.SIGNALS.append(self.SIGNAL_ACTION_SELECT_DB)
        urwid.connect_signal(self._table, self._table.SIGNAL_ROW_SELECTED, self.select_db)

    def __del__(self):
        urwid.disconnect_signal(self._table, self._table.SIGNAL_ROW_SELECTED,
                self.select_db)
        super().__del__()

    def select_db(self, emitter, row):
        database = row[0]
        urwid.emit_signal(self, self.SIGNAL_ACTION_SELECT_DB, self, database)

    def refresh(self, connection, **kwargs):
        if 'force_refresh' in kwargs and kwargs['force_refresh'] == True or self._model.last_error:
            self._model.reload()

    def search_db(self, db, pos=0, reverse=False):
        result = self._model.search(db, col_index=0, pos=pos, reverse=reverse)
        if result is None:
            return
        index, row = result
        self._table.focus_row(index)
        return (index, row)
