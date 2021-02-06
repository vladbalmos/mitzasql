# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid
from .table import Table
from ...db.model import TableModel as MysqlTableModel

class MysqlTable(Table):
    def __init__(self, model):
        if not isinstance(model, MysqlTableModel):
            raise TypeError("Wrong model type")
        super().__init__(model)

        urwid.connect_signal(model, model.SIGNAL_NEW_DATA, self.render_more)

    def __del__(self):
        urwid.disconnect_signal(self._model, self._model.SIGNAL_NEW_DATA, self.render_more)
        super().__del__()

    def render_more(self, model, data, data_length):
        for row in data:
            self._body.add_row(row)

    def _scroll_rows(self):
        if self._model.loaded_rowcount < len(self._model):
            remaining_rows_to_scroll = (self._model.loaded_rowcount - 1) - self._focused_row_index

            if remaining_rows_to_scroll > 0 and remaining_rows_to_scroll < 50:
                self._model.load_next_set()
            elif remaining_rows_to_scroll < 0:
                self._model.load_more(self._focused_row_index)

        if self._focused_row_index <= (self._model.loaded_rowcount - 1):
            return super()._scroll_rows()

