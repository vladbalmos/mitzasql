# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .info_widget import InfoWidget

class TableInfoWidget(InfoWidget):
    def __init__(self, model):
        self._model = model;
        head_section = self._create_head_section()
        body_section = self._create_body_section()

        contents = [head_section]
        contents.extend(body_section)
        super().__init__(contents)

    @property
    def name(self):
        return u'Table {0}'.format(self._model['table']['TABLE_NAME'])

    def _create_head_section(self):
        grid = []

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Name'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['table']['TABLE_NAME']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Comment'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['table']['TABLE_COMMENT']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Auto increment'),
            'editbox:label')))
        auto_increment = self._model['table']['AUTO_INCREMENT']
        if auto_increment is None:
            auto_increment = u'NULL'
        else:
            auto_increment = str(auto_increment)
        contents.append(urwid.AttrMap(urwid.Text(auto_increment), 'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Collation'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['table']['TABLE_COLLATION']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Engine'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['table']['ENGINE']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Row format'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['table']['ROW_FORMAT']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        grid = urwid.GridFlow(grid, cell_width=40, h_sep=1, v_sep=1,
                align='left')
        return grid

    def _create_body_section(self):
        body = []
        body.append(urwid.Divider('-'))
        body.append(urwid.AttrMap(urwid.Text(self._model['create_code']), 'default'))
        body.append(urwid.Text(''))
        return body
