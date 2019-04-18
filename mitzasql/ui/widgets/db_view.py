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
from mitzasql.ui.widgets.cmd_proc import (BaseCmdProcessor, SearchCmdProcessor)

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

    def search_db(self, db, pos=0, reverse=False):
        result = self._model.search(db, col_index=0, pos=pos, reverse=reverse)
        if result is None:
            return
        index, row = result
        self._table.focus_row(index)
        return (index, row)
