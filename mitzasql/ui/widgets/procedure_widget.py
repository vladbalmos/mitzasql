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

from mitzasql.ui.widgets.emacs_edit import EmacsEdit
import mitzasql.ui.utils as utils

class ProcedureWidget(urwid.ListBox):
    SIGNAL_ESCAPE = 'escape'

    def __init__(self, model):
        self._model = model;
        head_section = self._create_head_section()
        body_section = self._create_body_section()

        contents = [head_section]
        contents.extend(body_section)
        super().__init__(contents)
        urwid.register_signal(self.__class__, [self.SIGNAL_ESCAPE])

    @property
    def name(self):
        return u'{0} {1}'.format(self._model['type'], self._model['name'])

    def keypress(self, size, key):
        key = utils.vim2emacs_translation(key)
        if key == 'esc':
            urwid.emit_signal(self, self.SIGNAL_ESCAPE, self)
            return

        return super().keypress(size, key)

    def _create_head_section(self):
        grid = []

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Name'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['name']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Definer'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['definer']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Type'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['type']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Data access'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['sql_data_access']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        if (self._model['type'] == 'FUNCTION'):
            contents = []
            contents.append((18, urwid.AttrMap(urwid.Text(u'Returns'),
                'editbox:label')))
            contents.append(urwid.AttrMap(urwid.Text(self._model['returns']),
                'editbox'))
            grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'SQL Security'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['security_type']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Is deterministic?'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['is_deterministic']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        grid = urwid.GridFlow(grid, cell_width=40, h_sep=1, v_sep=1,
                align='left')
        return grid

    def _create_body_section(self):
        body = []
        body.append(urwid.Divider('-'))
        body.append(urwid.AttrMap(urwid.Text('Params'), 'default'))

        param_list = self._model['param_list'].decode(encoding='utf8').split(',')
        for param in param_list:
            body.append(urwid.AttrMap(urwid.Text(param.strip()), 'editbox'))
        body.append(urwid.Divider('-'))

        if len(self._model['comment']):
            body.append(urwid.AttrMap(urwid.Text(u'Comment: ' +
                self._model['comment'].decode(encoding='utf8')),
                'default'))
            body.append(urwid.Divider('-'))
        body.append(urwid.AttrMap(urwid.Text(self._model['body_utf8']),
            'default'))
        return body
