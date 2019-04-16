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

from mitzasql.state_machine import StateMachine
from mitzasql.ui.screens.screen import Screen
from mitzasql.ui.widgets.saved_sessions_list import SavedSessionsList
from mitzasql.ui.widgets.edit_session_form import EditSessionForm
from .widgets_factory import WidgetsFactory
from . import states

class SessionSelect(Screen):
    """The session select UI screen

    Implements the logic for creating, editing, deleting and selecting the
    session to connect to. When the user selects a session to connect to, the
    screen calls the main application instance with the session name or
    connection details.
    Child widgets are created using a widget factory and their state is managed
    with the help of a FSM"""

    # Signals handled by the main application instance
    SIGNAL_TEST_CONNECTION = 'test_connection'
    SIGNAL_CONNECT = 'connect'

    def __init__(self, sessions_registry):
        super().__init__([self.SIGNAL_CONNECT, self.SIGNAL_TEST_CONNECTION])
        self._sessions_registry = sessions_registry
        self._state_machine = self._init_state_machine()
        self._widgets_factory = WidgetsFactory(self._state_machine)
        self._state_machine.set_initial_state(states.STATE_INITIAL)
        self._state_machine.run()

    def __del__(self):
        self.focused_widget = None
        self.view = None
        self._widgets_factory = None

    def _init_state_machine(self):
        state_machine = StateMachine('session_select')
        state_machine.add_state(states.STATE_INITIAL, self.initial_state, {
            'has_sessions': states.STATE_SHOW_SESSIONS_LIST,
            'no_sessions': states.STATE_SHOW_CREATE_SESSION_DIALOG
            })
        state_machine.add_state(states.STATE_SHOW_CREATE_SESSION_DIALOG,
                self.show_create_new_session_dialog, {
                    'yes': states.STATE_SHOW_EDIT_SESSION_FORM,
                    'quit': states.STATE_QUIT
                    })
        state_machine.add_state(states.STATE_SHOW_SESSIONS_LIST,
                self.show_sessions_list, {
                    'quit': states.STATE_QUIT,
                    'create': states.STATE_SHOW_EDIT_SESSION_FORM,
                    'edit': states.STATE_SHOW_EDIT_SESSION_FORM,
                    'delete': states.STATE_DELETE_SESSION,
                    'connect': states.STATE_CONNECT
                    })
        state_machine.add_state(states.STATE_QUIT, self.quit)
        state_machine.add_state(states.STATE_CANCEL_EDIT_SESSION,
                self.cancel_edit_session, {
                    'quit': states.STATE_QUIT,
                    'show_sessions': states.STATE_SHOW_SESSIONS_LIST
                    })
        state_machine.add_state(states.STATE_SHOW_EDIT_SESSION_FORM,
                self.show_edit_session_form, {
                    'save': states.STATE_SAVE_SESSION,
                    'test': states.STATE_TEST_CONNECTION,
                    'cancel': states.STATE_CANCEL_EDIT_SESSION,
                    'connect': states.STATE_CONNECT
                    })
        state_machine.add_state(states.STATE_SAVE_SESSION,
                self.save_connection, {
                    'invalid': states.STATE_SHOW_EDIT_SESSION_FORM,
                    'valid': states.STATE_SHOW_SESSIONS_LIST
                    })
        state_machine.add_state(states.STATE_DELETE_SESSION,
                self.delete_session, {
                    'deleted': states.STATE_INITIAL
                    })
        state_machine.add_state(states.STATE_TEST_CONNECTION,
                self.test_connection, {
                    'invalid': states.STATE_SHOW_EDIT_SESSION_FORM,
                    'error': states.STATE_SHOW_EDIT_SESSION_FORM,
                    'success': states.STATE_SHOW_EDIT_SESSION_FORM
                    })
        state_machine.add_state(states.STATE_CONNECT, self.connect, {
                    'error_goto_form': states.STATE_SHOW_EDIT_SESSION_FORM,
                    'error_goto_list': states.STATE_SHOW_SESSIONS_LIST
                    })

        return state_machine

    def initial_state(self):
        if self._sessions_registry.is_empty():
            self._state_machine.change_state('no_sessions')
            return

        self._state_machine.change_state('has_sessions')

    def cancel_edit_session(self, *args, **kwargs):
        if self._sessions_registry.is_empty():
            self._state_machine.change_state('quit')
            return
        self._state_machine.change_state('show_sessions')

    def show_create_new_session_dialog(self, *args, **kwargs):
        self.focused_widget = self._widgets_factory.create('create_session_dialog')
        self.view.original_widget = urwid.Filler(urwid.Padding(self.focused_widget, align='center',
            width=('relative', 50)))

    def show_connection_error(self, *args, **kwargs):
        self.focused_widget = self._widgets_factory.create('dialog', u'Error', title=u'Connection error')
        self.view.original_widget = urwid.Filler(urwid.Padding(self.focused_widget, align='center', width=('relative', 50)))

    def show_sessions_list(self, *args, list_has_message=False):
        sessions = self._sessions_registry.sessions
        self.focused_widget = self._widgets_factory.create('sessions_list', sessions)
        self.view.original_widget = urwid.Filler(self.focused_widget)
        if list_has_message is False:
            self.focused_widget.clear_status_message()

    def delete_session(self, emitter, action):
        session_name = emitter.session
        del self._sessions_registry[session_name]
        self._sessions_registry.save()
        self._state_machine.change_state('deleted')

    def show_edit_session_form(self, *args, form_has_message=False, form_data={}):
        new_session = True
        if len(args) == 2:
            emitter, action = args
            if isinstance(emitter, SavedSessionsList) and action == 'Edit':
                new_session = False
                session_name = emitter.session
                form_data = self._sessions_registry[session_name]
                form_data['name'] = session_name
            elif isinstance(emitter, SavedSessionsList) and action == 'New':
                if form_has_message is False:
                    form_data = {}

        form = self._widgets_factory.create('create_session_form', form_data)

        if new_session is True:
            form_title = 'Create session'
        else:
            form_title = 'Edit session'

        form.editing_new_session = new_session
        form.title = form_title

        self.focused_widget = form
        self.view.original_widget = urwid.Filler(self.focused_widget)

        if form_has_message is False:
            form.clear_status_message()
            form.reset_focus()

    def test_connection(self, *args, **kwargs):
        form, *args = args
        form_data = form.data

        validation_error = self.validate_connection_data(form_data)
        if validation_error is not None:
            form.set_status_message(validation_error, error=True)
            self._state_machine.change_state('invalid',
                    form_has_message=True, form_data=form_data)
            return

        form.clear_status_message()
        urwid.emit_signal(self, self.SIGNAL_TEST_CONNECTION, self, form_data)

    def connect(self, *args, **kwargs):
        widget, *args = args

        if isinstance(widget, SavedSessionsList):
            session_name = widget.session
            urwid.emit_signal(self, self.SIGNAL_CONNECT, self, session_name)
            return

        if isinstance(widget, EditSessionForm):
            data = widget.data
            validation_error = self.validate_connection_data(data)
            if validation_error is not None:
                widget.set_status_message(validation_error, error=True)
                self._state_machine.change_state('error_goto_form',
                        form_has_message=True, form_data=data)
                return
            urwid.emit_signal(self, self.SIGNAL_CONNECT, self, None, data)
            return

        raise RuntimeError('The current widget should not trigger a connect signal: {0}'.format(str(widget)))


    def set_connection_result(self, result, error=None, session_name=None, connection_data=None):
        if result is False:
            self.focused_widget.set_status_message(error, error=True)
            if session_name is None:
                self._state_machine.change_state('error_goto_form',
                        form_has_message=True, form_data=connection_data)
            else:
                self._state_machine.change_state('error_goto_list',
                        list_has_message=True)
            return
        # nothing to do if result is True, our job is done

    def set_progress(self, message):
        widget = self.focused_widget
        widget.set_status_message(message)

    def set_connection_test_result(self, result, error=None):
        form = self.focused_widget
        form_data = form.data
        if result is False:
            form.set_status_message(error, error=True)
            self._state_machine.change_state('error', form_has_message=True,
                    form_data=form_data)
            return
        form.set_status_message(u'Connection was successful')
        self._state_machine.change_state('success', form_data=form_data,
                form_has_message=True)

    def save_connection(self, *args, **kwargs):
        form, *args = args
        form_data = form.data

        validation_error = self.validate_connection_data(form_data)
        if validation_error is not None:
            form.set_status_message(validation_error, error=True)
            self._state_machine.change_state('invalid',
                    form_has_message=True, form_data=form_data)
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
        self._state_machine.change_state('valid')

    def validate_connection_data(self, data):
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
