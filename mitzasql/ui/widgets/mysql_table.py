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

from .table import Table

from mitzasql.db.model import TableModel as MysqlTableModel

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

