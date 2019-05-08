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

import pickle
import hashlib
import urwid
import time
import sys

from mitzasql.ui import utils
from mitzasql.logger import logger

class InputProcessor():
    '''
    Implements support for VIM style keys & basic commands.

    Supported keys:
        j,k - scroll 1 row up/down
        h,l - scroll 1 column left/right
        ctrl-[u/d] - scroll rows page up/down
        0 - go to first column
        $ - go to last column
        G - go to last row

    Supported commands:
        [number]j/k/h/l - scroll [number] rows/columns
        gg - go to first row
    '''
    def __init__(self):
        self._last_key_press = None
        self._pending_command = None

        self._keys_direction = {
                'home': 'up',
                'ctrl u': 'up',
                'up' : 'up',
                'k': 'up',
                'page up': 'up',

                'end': 'down',
                'down': 'down',
                'j': 'down',
                'ctrl d': 'down',
                'G': 'down',
                'page down': 'down',

                'left': 'left',
                '0': 'left',
                'h': 'left',
                'ctrl left': 'left',

                'right': 'right',
                '$': 'right',
                'l': 'right',
                'ctrl right': 'right'
                }

        self._single_offset_keys = ['up', 'down', 'left', 'right', 'j', 'k', 'h', 'l']
        self._max_offset_keys = ['home', 'end', 'ctrl left', 'ctrl right', '0', '$', 'G']
        self._page_offset_keys = ['page up', 'page down', 'ctrl u', 'ctrl d']

        self._digit_keys = [str(i) for i in range(1, 10)]
        self._command_keys = ['g']
        self._command_keys.extend(self._digit_keys)

    def process_key(self, key):
        if not self._pending_command:
            if key in self._single_offset_keys:
                return (self._keys_direction[key], 1)

            if key in self._max_offset_keys:
                direction = self._keys_direction[key]
                return (direction, sys.maxsize)

            if key in self._page_offset_keys:
                direction = self._keys_direction[key]
                return (direction, 'page')

            if key in self._command_keys:
                self._last_key_press = time.time()
                self._pending_command = key
                return (None, None)

            return (None, None)

        diff = time.time() - self._last_key_press
        if diff > self._timeout(key):
            self._clear_pending_command()
            return (None, None)

        command = self._process_command(key)
        return (None, None, command)


    def _timeout(self, key):
        if self._pending_command.isdigit():
            return 1
        return 0.25

    def _clear_pending_command(self):
        self._pending_command = None
        self._last_key_press = None

    def _process_command(self, key):
        if key == 'esc':
            self._clear_pending_command()
            return

        if self._pending_command.isdigit() and key.isdigit():
            self._pending_command += key
            return

        if self._pending_command.isdigit() and not key.isdigit():
            offset = int(self._pending_command)
            self._clear_pending_command()

            if not key in self._keys_direction:
                return
            return ('scroll', self._keys_direction[key], offset)


        if self._pending_command == 'g' and key == 'g':
            self._clear_pending_command()
            return ('scroll', 'up', sys.maxsize)

class TCell(urwid.Text):
    def __init__(self, content, width, separator=True, align='left', separator_attr=None):
        self.separator = separator
        self._content = content
        self._align = align
        self._width = width
        self._separator_attr = separator_attr

        content = self._format_content()
        super().__init__(content, 'left', 'clip')

    def _format_content(self):
        content_attr = None
        if not isinstance(self._content, tuple):
            content = str(self._content)
        else:
            content_attr = self._content[0]
            content = str(self._content[1])

        if self.separator is True:
            content_max_len = self._width - 1
        else:
            content_max_len = self._width

        if len(content) > content_max_len:
            content = content[0:content_max_len - 1]
            content += chr(187)
        else:
            if self._align == 'left':
                content = content.ljust(content_max_len)
            else:
                content = content.rjust(content_max_len)

        if content_attr is not None:
            content = (content_attr, content)

        if self.separator is True:
            if self._separator_attr is not None:
                sep = (self._separator_attr, chr(124))
            else:
                sep = chr(124)
            if isinstance(content, list):
                content.append(sep)
            else:
                content = [content, sep]
        return content

    def resize(self, width):
        self._width = width
        content = self._format_content()
        self.set_text(content)

class TCellText(TCell):
    def __init__(self, content, width, separator=True):
        if isinstance(content, set):
            content = str(content)
        content = content.replace("\n", "\\n")
        super().__init__(content, width, separator)

class TCellNumber(TCell):
    def __init__(self, content, width, separator=True):
        super().__init__(content, width, separator, align='right')

class TCellNull(TCell):
    def __init__(self, width, column_info, separator=True):
        if column_info['is_int'] is True or column_info['is_real'] is True:
            align = 'right'
        else:
            align = 'left'
        content = ('tcell_null_unfocused', u'(NULL)')
        super().__init__(content, width, separator, align=align)

class TCellBinary(TCell):
    def __init__(self, content, width, separator=True):
        if not isinstance(content, str):
            try:
                content = content.decode(encoding='utf8')
            except:
                content = content.hex();

        if isinstance(content, str):
            content = content.replace("\n", "\\n")
        super().__init__(content, width, separator)

class TCellSpatial(TCell):
    def __init__(self, content, width, separator=True):
        if isinstance(content, str):
            content = content.replace("\n", "\\n")
        elif isinstance(content, bytearray):
            content = content.hex();
        super().__init__(content, width, separator)


class TRow(urwid.Columns):
    MIN_COL_LENGTH = 3
    MAX_COL_LENGTH = 80

    def __init__(self, cols, selectable=True):
        self._selectable = selectable
        super().__init__(cols, dividechars=1)

    def selectable(self):
        return self._selectable

    def keypress(self, size, key):
        return key

    def resize(self, col_index, increment):
        cell, options = self.contents[col_index]

        width = int(options[1]) + increment
        if width < self.MIN_COL_LENGTH or width > self.MAX_COL_LENGTH:
            return
        cell.resize(width)

        options = self.options('given', width, False)
        self.contents[col_index] = (cell, options)
        return width

    def render(self, size, focus=False):
        for col in self.contents:
            if not isinstance(col[0], TCellNull):
                continue
            text, attr = col[0].get_text()
            if focus is True:
                attr = 'tcell_null_focused'
            else:
                attr = 'tcell_null_unfocused'

            if col[0].separator is True:
                text = [(attr, text[0:-1]), text[-1:]]
            else:
                text = (attr, text)
            col[0].set_text(text)
        return super().render(size, focus)

class THeader(TRow):
    def __init__(self, columns):
        self.cell_sizes = []
        self._cols_hash = self._get_cols_hash(columns)
        cols = self._create_cols(columns)
        super().__init__(cols, False)

    def _get_cols_hash(self, columns):
        serialized = pickle.dumps(columns)
        m = hashlib.sha256()
        m.update(serialized)
        hsh = m.digest()
        return hsh

    def _create_cols(self, columns):
        cols = []
        index = 0
        columns_count = len(columns)

        for info in columns:
            name = info['name']
            size = info['max_len']
            self.cell_sizes.append(size)

            if index < columns_count - 1:
                separator = True
            else:
                separator = False

            if info['is_int'] is True or info['is_real'] is True:
                align = 'right'
            else:
                align = 'left'

            cell = TCell(name, size, separator, align=align, separator_attr='theader_sep')
            cols.append((size, cell))
            index += 1
        return cols

    def refresh(self, columns):
        cols_hash = self._get_cols_hash(columns)
        if cols_hash == self._cols_hash:
            return
        self._cols_hash = cols_hash
        self.cell_sizes = []
        self.contents.clear()
        cols = self._create_cols(columns)
        for width, widget in cols:
            col_size = self.options(width_type='given', width_amount=width)
            self.contents.append((widget, col_size))

    def resize(self, col_index, increment):
        width = super().resize(col_index, increment)
        if width is not None:
            self.cell_sizes[col_index] = width
        return width

class TBody(urwid.ListBox):
    KEYPRESS = 'keypress'

    def __init__(self, columns_list, cell_sizes, rows=[]):
        self._columns_list = columns_list
        self._cell_sizes = cell_sizes

        urwid.register_signal(self.__class__, self.KEYPRESS)
        super().__init__(urwid.SimpleFocusListWalker(rows))

    def set_columns(self, columns_list, cell_sizes):
        self._columns_list = columns_list
        self._cell_sizes = cell_sizes

    def update_col_width(self, col_index, width):
        self._cell_sizes[col_index] = width

    def clear(self):
        self.body.clear()

    def add_row(self, row_data):
        row = self.make_row(row_data)
        self.body.append(row)

    def __iter__(self):
        for row in self.body:
            yield row

    @property
    def focused_row(self):
        row, index = self.body.get_focus()
        return row.original_widget

    def make_row(self, columns):
        cols = []
        index = 0
        columns_count = len(columns)

        for index, value in enumerate(columns):
            column_info = self._columns_list[index]
            cell_size = self._cell_sizes[index]

            if index < columns_count - 1:
                separator = True
            else:
                separator = False

            cell = self._make_cell(value, cell_size, separator, column_info)

            cols.append((cell_size, cell))
        row = urwid.AttrMap(TRow(cols), 'default', focus_map='trow_focused')
        return row

    def _make_cell(self, value, size, separator, column_info):
        if value is None:
            cell = TCellNull(size, column_info, separator)
        elif column_info['is_binary'] is True:
            cell = TCellBinary(value, size, separator)
        elif column_info['is_int'] is True or column_info['is_real'] is True:
            cell = TCellNumber(value, size, separator)
        elif column_info['is_text'] is True:
            cell = TCellText(value, size, separator)
        elif column_info['is_spatial'] is True:
            cell = TCellSpatial(value, size, separator)
        else:
            cell = TCell(value, size, separator)
        return cell

    def keypress(self, size, key):
        '''Emit a signal with the key and size to be handled in the parent

        The reason for this is to get the inner size of the table
        Disable only the 'up' and 'down' keys due to interfering
        with other parent pile containers
        '''
        urwid.emit_signal(self, self.KEYPRESS, self, size, key)
        if key == 'up' or key == 'down':
            return
        return key

class Table(urwid.Frame):
    SIGNAL_ROW_SELECTED = 'selected'
    SIGNALS = [SIGNAL_ROW_SELECTED]

    def __init__(self, model):
        self._model = model
        self._rowcount = len(self._model)
        self._header = THeader(self._model.columns)
        self._body = self.make_body()
        self._footer = urwid.Text('')
        self._widget_size = None
        self._visible_columns = 0
        self._focused_row_index = 0
        self._focused_col_index = 0
        self._input_processor = InputProcessor()

        urwid.connect_signal(model, model.SIGNAL_LOAD, self.refresh)

        super().__init__(self._body,
                urwid.AttrMap(self._header, 'theader'),
                urwid.AttrMap(self._footer, 'tfooter'))
        urwid.register_signal(self.__class__, self.SIGNALS)
        self._update_footer()

    def __del__(self):
        urwid.disconnect_signal(self._model, self._model.SIGNAL_LOAD, self.refresh)
        urwid.disconnect_signal(self._body, self._body.KEYPRESS, self.on_body_keypress)
        self._body.clear()

    def focus_row(self, row_index):
        self._focused_row_index = row_index
        self._scroll_rows()

    def refresh(self, model):
        self._visible_columns = 0
        self._focused_row_index = 0
        self._focused_col_index = 0
        self._rowcount = len(self._model)
        utils.orig_w(self._header).refresh(self._model.columns)
        self._body.clear()
        self._body.set_columns(self._model.columns, utils.orig_w(self._header).cell_sizes)
        for row in self._model:
            self._body.add_row(row)
        self._update_footer()
        self._scroll_rows()

    def resize_col(self, col_index, increment=1):
        width = self._header.original_widget.resize(col_index, increment)

        if width is not None:
            self._body.update_col_width(col_index, width)

        for row in self._body.body:
            trow = row.original_widget
            trow.resize(col_index, increment)

    def _increment_col_index(self, offset, absolute=False):
        if absolute is False:
            new_index = self._focused_col_index + offset
        else:
            new_index = offset

        if new_index < 0:
            new_index = 0
        elif new_index < self._visible_columns - 1:
            new_index = self._visible_columns - 1

        if new_index > (len(self._model.columns) - 1):
            new_index = len(self._model.columns) - 1

        self._focused_col_index = new_index

    def _increment_row_index(self, offset, absolute=False):
        if absolute is False:
            new_index = self._focused_row_index + offset
        else:
            new_index = offset

        if new_index < 0:
            new_index = 0

        if new_index > (self._rowcount - 1):
            new_index = self._rowcount - 1

        self._focused_row_index = new_index

    def make_body(self):
        body = TBody(columns_list=self._model.columns,
                cell_sizes=self._header.cell_sizes)

        urwid.connect_signal(body, body.KEYPRESS, self.on_body_keypress)
        for row in self._model:
            body.add_row(row)
        return body

    def on_body_keypress(self, emitter, size, key):
        self._widget_size = size

        if not self._rowcount:
            return

        self._detect_visible_columns_count()

        row, index = self._body.body.get_focus()
        self._focused_row_index = index

        if key == 'enter':
            urwid.emit_signal(self, self.SIGNAL_ROW_SELECTED, self,
                    self._model[index])

        direction, offset, *command  = self._input_processor.process_key(key)

        if direction is None and len(command) and command[0] is None:
            return

        if len(command):
            command = command.pop()
            if isinstance(command, tuple):
                if command[0] == 'scroll':
                    direction, offset = command[1:]
                else:
                    raise RuntimeError('Unimplemented command {0}'.format(command[0]))

        if offset == 'page':
            offset = size[1] - 2

        if direction == 'down':
            self._scroll_down(offset)
        elif direction == 'up':
            self._scroll_up(offset)
        elif direction == 'left':
            self._scroll_left(offset)
        elif direction == 'right':
            self._scroll_right(offset)

        self._update_footer()

    def _update_footer(self):
        rowcount = self._rowcount
        cols_count = len(self._model.columns)

        row_index = self._focused_row_index

        status = u'[{0}/{1}:{2}]'.format(row_index + 1, rowcount, cols_count)

        self._footer.original_widget.set_text(status)

    def _detect_visible_columns_count(self):
        focused_row = self._body.focused_row
        column_widths = focused_row.column_widths(self._widget_size)
        visible_columns = 0
        for width in column_widths:
            if width > 0:
                visible_columns += 1
        self._visible_columns = visible_columns

    def _scroll_down(self, offset):
        self._increment_row_index(offset)
        self._scroll_rows()

    def _scroll_up(self, offset):
        self._increment_row_index(-1 * offset)
        self._scroll_rows()

    def _scroll_left(self, offset):
        if self._focused_col_index < self._visible_columns - 1:
            self._focused_col_index = self._visible_columns - 1
        else:
            self._increment_col_index(-1 * offset)

        self._scroll_columns()

    def _scroll_right(self, offset):
        if self._focused_col_index == 0:
            self._increment_col_index(self._visible_columns - 1 + offset,
                    absolute=True)
        else:
            self._increment_col_index(1 * offset)

        self._scroll_columns()

    def _scroll_columns(self):
        for row in self._body.body:
            row.original_widget.focus_position = self._focused_col_index
        self._header.original_widget.focus_position = self._focused_col_index

    def _scroll_rows(self):
        if self._focused_row_index >= len(self._model):
            return
        self._body.set_focus(self._focused_row_index)
        # Enforce the column focus because sometimes it resets to 0 and screws up
        # the rendering
        self._scroll_columns()
