# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from ..utils import orig_w
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

    def __init__(self, data={}, editing_new_session=True):

        actions = [
            ('F1', u'F1 Save', self.SIGNAL_SAVE),
            ('F2', u'F2 Test connection', self.SIGNAL_TEST),
            ('F3', u'F3 Connect', self.SIGNAL_CONNECT),
            ('Esc', u'Esc Cancel', self.SIGNAL_CANCEL)
            ]

        self.editing_new_session = editing_new_session
        self._old_session_name = None

        if len(data) == 0:
            self._data = {
                    'name': '',
                    'host': '',
                    'port': '',
                    'username': '',
                    'password': '',
                    'database': ''
                    }
        else:
            self._data = data
        self._input_elements = {}
        self._focus_position = 0
        self._name_field_container = None
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
        if not self.editing_new_session:
            name_is_read_only = True
            name_attr = 'editbox:label'
        else:
            name_is_read_only = False
            name_attr = 'editbox'

        name_label = urwid.Text(u'Session name:')
        name_edit = EmacsEdit(edit_text=self['name'],
                read_only=name_is_read_only)
        name_edit.value_name = 'name'
        self._input_elements['name'] = name_edit
        urwid.connect_signal(name_edit, 'postchange', self.on_input_change)
        name_edit = urwid.AttrMap(name_edit, name_attr)

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

        if not name_is_read_only:
            row = urwid.Columns([(15, name_label), (32, name_edit),
                urwid.Text(u'Required')], dividechars=1)
        else:
            row = urwid.Columns([(15, name_label), (32, name_edit)], dividechars=1)
        self._name_field_container = row
        contents.append(row)

        contents.append(urwid.Divider())

        row = urwid.Columns([(15, host_label), (32, host_edit),
            urwid.Text(u'Must start with tcp:// or unix://')], dividechars=1)
        contents.append(row)

        if name_is_read_only:
            self._focus_position = 2

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

    def refresh(self, data, editing_new_session=None):
        self._data = data
        self.editing_new_session = editing_new_session
        for name, widget in self._input_elements.items():
            if name not in data:
                value = ''
            else:
                value = data[name]
            widget.edit_text = value
        self._old_session_name = None

        if editing_new_session == None:
            return

        if not editing_new_session:
            self._toggle_name_read_only(True)
            return

        self._toggle_name_read_only(False)

    def _toggle_name_read_only(self, state):
        name_field = self._name_field_container.contents[1][0]

        if orig_w(name_field).read_only == state:
            return

        if state:
            orig_w(name_field).read_only = True
            name_field.set_attr_map({None: 'editbox:label'})
            del self._name_field_container.contents[2]
            self._focus_position = 2
        else:
            orig_w(name_field).read_only = False
            name_field.set_attr_map({None: 'editbox'})

            if len(self._name_field_container.contents) == 2:
                options = self._name_field_container.options('pack')
                self._name_field_container.contents.append((urwid.Text(u'Required'), options))
                self._focus_position = 0
        self._name_field_container.focus_position = 1
        self.reset_focus()

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

    def reset_focus(self):
        self._form.focus_position = self._focus_position

