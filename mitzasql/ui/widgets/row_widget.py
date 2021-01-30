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

from .info_widget import InfoWidget

class RowWidget(InfoWidget):
    def __init__(self, row, columns):
        self._row = row;
        self._columns = columns
        contents = self._create_contents()
        super().__init__([contents])

    @property
    def name(self):
        return u'Row data'

    def _create_contents(self):
        grid = []

        index = 0
        for item in self._row:
            if item is None:
                cell_data = u'NULL'
            else:
                if isinstance(item, bytearray):
                    try:
                        cell_data = item.decode(encoding='utf8')
                    except:
                        cell_data = item.hex()
                else:
                    cell_data = str(item)
            cell_name = str(self._columns[index]['name'])

            contents = []
            contents.append((40, urwid.AttrMap(urwid.Text(cell_name), 'editbox:label')))
            contents.append(urwid.AttrMap(urwid.Text(cell_data),
                'editbox'))
            grid.append(urwid.Columns(contents))
            index += 1

        grid = urwid.GridFlow(grid, cell_width=80, h_sep=1, v_sep=1,
                align='left')
        return grid
