# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .info_widget import InfoWidget

class ViewInfoWidget(InfoWidget):

    def __init__(self, model):
        self._model = model;
        head_section = self._create_head_section()
        body_section = self._create_body_section()

        contents = [head_section]
        contents.extend(body_section)
        super().__init__(contents)

    @property
    def name(self):
        return u'View {0}'.format(self._model['TABLE_NAME'])

    def _create_head_section(self):
        grid = []

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Name'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['TABLE_NAME']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Definer'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['DEFINER']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'SQL Security'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['SECURITY_TYPE']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        grid = urwid.GridFlow(grid, cell_width=40, h_sep=1, v_sep=1,
                align='left')
        return grid

    def _create_body_section(self):
        body = []
        body.append(urwid.Divider('-'))
        body.append(urwid.AttrMap(urwid.Text(self._model['VIEW_DEFINITION']),
            'default'))
        body.append(urwid.Text(''))
        return body
