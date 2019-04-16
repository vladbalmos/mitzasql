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

from .action_bar_pile_container import ActionBarPileContainer
from .emacs_edit import EmacsEdit
from .emacs_intedit import EmacsIntEdit

class EditSessionForm(ActionBarPileContainer):
    """Create & edit sessions"""

    # Signals handled by the select session UI screen
    SIGNAL_SAVE = 'save'
    SIGNAL_TEST = 'test'
    SIGNAL_CONNECT = 'connect'
    SIGNAL_CANCEL = 'cancel'

    def __init__(self, data={}):

        actions = [
            ('F1', u'F1 Save', self.SIGNAL_SAVE),
            ('F2', u'F2 Test connection', self.SIGNAL_TEST),
            ('F3', u'F3 Connect', self.SIGNAL_CONNECT),
            ('Esc', u'Esc Cancel', self.SIGNAL_CANCEL)
            ]

        self.editing_new_session = True
        self._old_session_name = None

        if len(data) == 0:
            data = {
                    'name': '',
                    'host': '',
                    'port': '',
                    'username': '',
                    'password': '',
                    'database': ''
                    }
        self._data = data
        self._input_elements = {}
        self._form = self._create_form()

        super().__init__(self._form, actions, line_box=True,
                line_box_title=u'Create Session')

    @property
    def title(self):
        return self._container.get_title()

    @title.setter
    def title(self, title):
        self._container.set_title(title)

    def _create_form(self):
        name_label = urwid.Text(u'Session name:')
        name_edit = EmacsEdit(edit_text=self['name'])
        name_edit.value_name = 'name'
        self._input_elements['name'] = name_edit
        urwid.connect_signal(name_edit, 'postchange', self.on_input_change)
        name_edit = urwid.AttrMap(name_edit, 'editbox')

        host_label = urwid.Text(u'Host:')
        host_edit = EmacsEdit(edit_text=self['host'])
        host_edit.value_name = 'host'
        self._input_elements['host'] = host_edit
        urwid.connect_signal(host_edit, 'postchange', self.on_input_change)
        host_edit = urwid.AttrMap(host_edit, 'editbox')

        port_label = urwid.Text(u'Port:')
        port_edit = EmacsIntEdit(default=self['port'])
        port_edit.value_name = 'port'
        self._input_elements['port'] = port_edit
        urwid.connect_signal(port_edit, 'postchange', self.on_input_change)
        port_edit = urwid.AttrMap(port_edit, 'editbox')

        username_label = urwid.Text(u'Username:')
        username_edit = EmacsEdit(edit_text=self['username'])
        username_edit.value_name = 'username'
        self._input_elements['username'] = username_edit
        urwid.connect_signal(username_edit, 'postchange', self.on_input_change)
        username_edit = urwid.AttrMap(username_edit, 'editbox')

        password_label = urwid.Text(u'Password:')
        password_edit = EmacsEdit(edit_text=self['password'], mask='*')
        password_edit.value_name = 'password'
        self._input_elements['password'] = password_edit
        urwid.connect_signal(password_edit, 'postchange', self.on_input_change)
        password_edit = urwid.AttrMap(password_edit, 'editbox')

        database_label = urwid.Text(u'Database:')
        database_edit = EmacsEdit(edit_text=self['database'])
        database_edit.value_name = 'database'
        self._input_elements['database'] = database_edit
        urwid.connect_signal(database_edit, 'postchange', self.on_input_change)
        database_edit = urwid.AttrMap(database_edit, 'editbox')

        contents = []

        row = urwid.Columns([(15, name_label), (32, name_edit),
            urwid.Text(u'Required')], dividechars=1)
        contents.append(row)

        contents.append(urwid.Divider())

        row = urwid.Columns([(15, host_label), (32, host_edit),
            urwid.Text(u'Must start with tcp:// or unix://')], dividechars=1)
        contents.append(row)

        contents.append(urwid.Divider())

        row = urwid.Columns([(15, port_label), (6, port_edit),
            urwid.Text(u'Required only for tcp:// connections')], dividechars=1)
        contents.append(row)

        contents.append(urwid.Divider())

        row = urwid.Columns([(15, username_label), (32, username_edit),
            urwid.Text(u'Required')], dividechars=1)
        contents.append(row)

        contents.append(urwid.Divider())

        row = urwid.Columns([(15, password_label), (32, password_edit)],
                dividechars=1)
        contents.append(row)

        contents.append(urwid.Divider())

        row = urwid.Columns([(15, database_label), (32, database_edit)],
                dividechars=1)
        contents.append(row)

        contents.append(urwid.Divider())

        pile = urwid.Pile(contents)
        return pile

    def __getitem__(self, name):
        if name in self._data:
            return self._data[name]
        return ''

    def refresh(self, data):
        self._data = data
        for name, widget in self._input_elements.items():
            if name not in data:
                value = ''
            else:
                value = data[name]
            widget.edit_text = value
        self._old_session_name = None

    def reset_focus(self):
        self._form.focus_position = 0

    @property
    def data(self):
        data = self._data.copy()

        if self.editing_new_session is False:
            data['old_name'] = self._old_session_name

        return data

    def on_input_change(self, emitter, old_value):
        if emitter.value_name == 'name' and self.editing_new_session is False:
            if self._old_session_name is None and 'name' in self._data:
                self._old_session_name = self._data['name']
        self._data[emitter.value_name] = emitter.edit_text

    def keypress(self, size, key):
        if key == 'tab':
            key = 'down'
        elif key == 'shift tab':
            key = 'up'
        return super().keypress(size, key)
