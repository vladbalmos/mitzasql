# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .info_widget import InfoWidget

class TriggerWidget(InfoWidget):
    def __init__(self, model):
        self._model = model;
        head_section = self._create_head_section()
        body_section = self._create_body_section()

        contents = [head_section]
        contents.extend(body_section)
        super().__init__(contents)

    @property
    def name(self):
        return u'Trigger {0}'.format(self._model['TRIGGER_NAME'])

    def _create_head_section(self):
        grid = []

        contents = []
        contents.append((10, urwid.AttrMap(urwid.Text(u'Name'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['TRIGGER_NAME']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((10, urwid.AttrMap(urwid.Text(u'Definer'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['DEFINER']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((10, urwid.AttrMap(urwid.Text(u'On table'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['EVENT_OBJECT_TABLE']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((10, urwid.AttrMap(urwid.Text(u'Timing'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['ACTION_TIMING']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        contents = []
        contents.append((10, urwid.AttrMap(urwid.Text(u'Event'),
            'editbox:label')))
        contents.append(urwid.AttrMap(urwid.Text(self._model['EVENT_MANIPULATION']),
            'editbox'))
        grid.append(urwid.Columns(contents))

        grid = urwid.GridFlow(grid, cell_width=40, h_sep=1, v_sep=1,
                align='left')
        return grid

    def _create_body_section(self):
        body = []
        body.append(urwid.Divider('-'))
        body.append(urwid.AttrMap(urwid.Text(self._model['ACTION_STATEMENT']),
            'default'))
        body.append(urwid.Text(''))
        return body
