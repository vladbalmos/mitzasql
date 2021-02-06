# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid
from .info_widget import InfoWidget

class ProcedureWidget(InfoWidget):
    def __init__(self, model):
        self._model = model;
        head_section = self._create_head_section()
        body_section = self._create_body_section()

        contents = [head_section]
        contents.extend(body_section)
        super().__init__(contents)

    @property
    def name(self):
        return u'{0} {1}'.format(self._model['ROUTINE_TYPE'],
                self._model['SPECIFIC_NAME'])

    def _create_head_section(self):
        grid = []

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Name'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['SPECIFIC_NAME']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Definer'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['DEFINER']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Type'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['ROUTINE_TYPE']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Data access'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['SQL_DATA_ACCESS']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        if (self._model['ROUTINE_TYPE'] == 'FUNCTION'):
            contents = []
            contents.append((18, urwid.AttrMap(urwid.Text(u'Returns'),
                'editbox:label')))
            contents.append(urwid.AttrMap(urwid.Text(self._model['DTD_IDENTIFIER']),
                'editbox'))
            grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'SQL Security'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['SECURITY_TYPE']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((18, urwid.AttrMap(urwid.Text(u'Is deterministic?'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['IS_DETERMINISTIC']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        grid = urwid.GridFlow(grid, cell_width=40, h_sep=1, v_sep=1,
                align='left')
        return grid

    def _create_body_section(self):
        body = []
        body.append(urwid.Divider('-'))
        body.append(urwid.AttrMap(urwid.Text('Params'), 'default'))

        if not isinstance(self._model['param_list'], str):
            param_list = self._model['param_list'].decode(encoding='utf8').split(',')
        else:
            param_list = self._model['param_list'].split(',')
        for param in param_list:
            body.append(urwid.AttrMap(urwid.Text(param.strip()), 'editbox'))
        body.append(urwid.Divider('-'))

        if len(self._model['ROUTINE_COMMENT']):
            comment = self._model['ROUTINE_COMMENT']
            if not isinstance(comment, str):
                comment = comment.decode(encoding='utf8')
            body.append(urwid.AttrMap(urwid.Text(u'Comment: ' + comment),
                'default'))
            body.append(urwid.Divider('-'))
        body.append(urwid.AttrMap(urwid.Text(self._model['ROUTINE_DEFINITION']),
            'default'))
        body.append(urwid.Text(''))
        return body
