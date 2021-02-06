# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

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
