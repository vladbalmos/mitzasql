# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from ..screen import Screen
from ...widgets.saved_sessions_list import SavedSessionsList
from ...widgets.edit_session_form import EditSessionForm
from ...widgets.create_new_session_dialog import CreateNewSessionDialog

class SessionSelect(Screen):
    """The session select UI screen

    Implements the logic for creating, editing, deleting and selecting the
    session to connect to. When the user selects a session to connect to, the
    screen calls the main application instance with the session name or
    connection details.
    """

    # Signals handled by the main application instance
    SIGNAL_TEST_CONNECTION = 'test_connection'
    SIGNAL_CONNECT = 'connect'

    def __init__(self, sessions_registry):
        super().__init__([self.SIGNAL_CONNECT, self.SIGNAL_TEST_CONNECTION])
        self._sessions_registry = sessions_registry
        self._edit_form_widget = None
        self._sessions_list = None
        self.show_inital_widget()

    def __del__(self):
        self.focused_widget = None
        self._edit_form_widget = None
        self.view = None

    def show_inital_widget(self, *args):
        if self._sessions_registry.is_empty():
            return self._show_create_new_session_dialog()

        return self.show_sessions_list()

    def show_sessions_list(self, *args):
        sessions = self._sessions_registry.sessions
        if not self._sessions_list:
            list_ = SavedSessionsList(sessions)
            urwid.connect_signal(list_, SavedSessionsList.SIGNAL_QUIT, self.quit)
            urwid.connect_signal(list_, SavedSessionsList.SIGNAL_CREATE_NEW, self.create_new_session)
            urwid.connect_signal(list_, SavedSessionsList.SIGNAL_CONNECT, self.connect)
            urwid.connect_signal(list_, SavedSessionsList.SIGNAL_EDIT, self.edit_session)
            urwid.connect_signal(list_, SavedSessionsList.SIGNAL_DELETE, self.delete_session)
            self._sessions_list = list_
        else:
            self._sessions_list.refresh(sessions)

        self.focused_widget = self._sessions_list
        self.view.original_widget = urwid.Filler(self.focused_widget)

    def _show_create_new_session_dialog(self, *args, **kwargs):
        dialog = CreateNewSessionDialog()

        urwid.connect_signal(dialog, CreateNewSessionDialog.SIGNAL_YES, self.show_edit_session_form)
        urwid.connect_signal(dialog, CreateNewSessionDialog.SIGNAL_QUIT, self.quit)

        self.focused_widget = dialog
        self.view.original_widget = urwid.Filler(urwid.Padding(self.focused_widget, align='center',
            width=('relative', 50)))

    def show_edit_session_form(self, *args):
        if not self._edit_form_widget:
            form = EditSessionForm()
            urwid.connect_signal(form, form.SIGNAL_SAVE, self.save_connection)
            urwid.connect_signal(form, form.SIGNAL_TEST, self.test_connection)
            urwid.connect_signal(form, form.SIGNAL_CONNECT, self.connect)
            urwid.connect_signal(form, form.SIGNAL_CANCEL, self.show_inital_widget)
            self._edit_form_widget = form

        self._edit_form_widget.clear_status_message()
        self._edit_form_widget.refresh({})
        self._edit_form_widget.reset_focus()
        self.focused_widget = self._edit_form_widget
        self.view.original_widget = urwid.Filler(self.focused_widget)

    def create_new_session(self, *args):
        self.show_edit_session_form()
        self._edit_form_widget.refresh({}, True)

    def edit_session(self, *args):
        session_name = self._sessions_list.session
        form_data = self._sessions_registry[session_name]
        form_data['name'] = session_name
        self.show_edit_session_form()
        self._edit_form_widget.refresh(form_data, False)

    def save_connection(self, *args):
        form = self._edit_form_widget
        form_data = form.data
        validation_error = self._validate_connection_data(form_data)

        if validation_error is not None:
            form.set_status_message(validation_error, error=True)
            return

        if 'old_name' in form_data and form_data['old_name'] is not None:
            # Handle update session name
            old_name = form_data['old_name']
            del form_data['old_name']
            self._sessions_registry.edit(old_name, form_data)
        else:
            if 'old_name' in form_data and form_data['old_name'] is None:
                del form_data['old_name']
            self._sessions_registry.add(form_data)
        self._sessions_registry.save()
        self.show_sessions_list()

    def test_connection(self, *args):
        form = self._edit_form_widget
        form_data = form.data
        validation_error = self._validate_connection_data(form_data)

        if validation_error is not None:
            form.set_status_message(validation_error, error=True)
            return

        form.clear_status_message()
        urwid.emit_signal(self, self.SIGNAL_TEST_CONNECTION, self, form_data)

    def connect(self, *args):
        widget, *args = args

        if isinstance(widget, SavedSessionsList):
            session_name = widget.session
            urwid.emit_signal(self, self.SIGNAL_CONNECT, self, session_name)
            return

        if isinstance(widget, EditSessionForm):
            data = widget.data
            validation_error = self._validate_connection_data(data)
            if validation_error is not None:
                widget.set_status_message(validation_error, error=True)
                return
            urwid.emit_signal(self, self.SIGNAL_CONNECT, self, None, data)
            return

        raise RuntimeError('The current widget should not trigger a connect signal: {0}'.format(str(widget)))

    def delete_session(self, emitter, action):
        session_name = emitter.session
        del self._sessions_registry[session_name]
        self._sessions_registry.save()
        self.show_inital_widget()

    def show_message(self, message):
        widget = self.focused_widget
        widget.set_status_message(message)

    def set_connection_test_result(self, result, error=None):
        form = self._edit_form_widget
        if result is False:
            form.set_status_message(error, error=True)
            return

        form.set_status_message(u'Connection was successful')

    def set_connection_result(self, result, error=None, session_name=None, connection_data=None):
        if result is False:
            self.focused_widget.set_status_message(error, error=True)
        # nothing to do if result is True, our job is done

    def _validate_connection_data(self, data):
        if len(data['name']) == 0:
            return u'Session name is required'

        if len(data['host']) == 0:
            return u'Host is required'

        host = data['host']
        if not host.startswith('tcp://') and not host.startswith('unix://'):
            return u'Host is missing protocol (tcp://, unix://)'

        host_is_tcp = False

        if host.startswith('tcp://'):
            host_is_tcp = True
            host = host[6:]
        elif host.startswith('unix://'):
            host = host[7:]

        if len(host) == 0:
            return u'Host must not be empty'

        if host_is_tcp is True and ('port' not in data or len(data['port']) == 0):
            return u'Port is required'

        if 'username' not in data or len(data['username']) == 0:
            return u'Username is required'

        return None
