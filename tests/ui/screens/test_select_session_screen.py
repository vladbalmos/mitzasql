import tempfile
import os
import pytest

from mitzasql.ui.screens.session_select import (session_select, states)
from mitzasql.ui.widgets.saved_sessions_list import SavedSessionsList
from mitzasql.ui.widgets.create_new_session_dialog import CreateNewSessionDialog
from mitzasql.ui.widgets.edit_session_form import EditSessionForm
from mitzasql.sessions_registry import SessionsRegistry

bad_connection_data_set = [
        {
            'data': {},
            'expected_message': u'Session name is required'
        },
        {
            'data': {
                'name': ''
                },
            'expected_message': u'Session name is required'
        },
        {
            'data': {
                'name': 'some name',
                },
            'expected_message': u'Host is required'
        },
        {
            'data': {
                'name': 'some name',
                'host': ''
                },
            'expected_message': u'Host is required'
        },
        {
            'data': {
                'name': 'some name',
                'host': 'unknown protocol'
                },
            'expected_message': u'Host is missing protocol (tcp://, unix://)'
        },
        {
            'data': {
                'name': 'some name',
                'host': 'tcp://'
                },
            'expected_message': u'Host must not be empty'
        },
        {
            'data': {
                'name': 'some name',
                'host': 'unix://'
                },
            'expected_message': u'Host must not be empty'
        },
        {
            'data': {
                'name': 'some name',
                'host': 'tcp://localhost'
                },
            'expected_message': u'Port is required'
        },
        {
            'data': {
                'name': 'some name',
                'host': 'tcp://localhost',
                'port': ''
                },
            'expected_message': u'Port is required'
        },
        {
            'data': {
                'name': 'some name',
                'host': 'tcp://localhost',
                'port': '3306'
                },
            'expected_message': u'Username is required'
        },
        {
            'data': {
                'name': 'some name',
                'host': 'tcp://localhost',
                'port': '3306',
                'username': ''
                },
            'expected_message': u'Username is required'
        },
        {
            'data': {
                'name': 'some name',
                'host': 'unix:///var/run/mysql.sock',
                'username': ''
                },
            'expected_message': u'Username is required'
        },
        ]

@pytest.fixture
def registry_with_a_session():
    sessions_file = tempfile.NamedTemporaryFile()
    registry = SessionsRegistry(sessions_file.name)
    registry.add({
        'name': 'Test session',
        'host': 'tcp://localhost',
        'port': '3306',
        'username': 'root',
        'password': 'root',
        'database': ''
        })
    return registry

@pytest.fixture
def empty_registry():
    sessions_file = tempfile.NamedTemporaryFile()
    registry = SessionsRegistry(sessions_file.name)
    return registry

@pytest.fixture(params=bad_connection_data_set)
def bad_connection_data(request):
    return request.param

@pytest.fixture
def good_connection_data():
    return {
            'name': 'Tcp connection',
            'host': 'tcp://localhost',
            'port': '3306',
            'username': 'root',
            'password': 'root',
            'database': 'mysql'
            }

def test_screen_displays_sessions_list(registry_with_a_session):
    sessions_select_screen = session_select.SessionSelect(registry_with_a_session)
    assert sessions_select_screen._state_machine.get_current_state() == states.STATE_SHOW_SESSIONS_LIST
    assert isinstance(sessions_select_screen.view.original_widget.body,
            SavedSessionsList) is True

def test_screen_shows_the_create_new_session_form(empty_registry):
    sessions_select_screen = session_select.SessionSelect(empty_registry)
    sessions_select_screen._state_machine.change_state('yes')
    assert sessions_select_screen._state_machine.get_current_state() == states.STATE_SHOW_EDIT_SESSION_FORM
    assert isinstance(sessions_select_screen.view.original_widget.body,
            EditSessionForm) is True

def test_screen_displays_create_new_session_dialog(empty_registry):
    sessions_select_screen = session_select.SessionSelect(empty_registry)
    assert sessions_select_screen._state_machine.get_current_state() == states.STATE_SHOW_CREATE_SESSION_DIALOG
    assert isinstance(sessions_select_screen.view.original_widget.body.original_widget,
            CreateNewSessionDialog) is True

def test_screen_shows_form_validation_error_on_create_new_session(empty_registry, bad_connection_data):
    sessions_select_screen = session_select.SessionSelect(empty_registry)

    sessions_select_screen._state_machine.change_state('yes')
    assert sessions_select_screen._state_machine.get_current_state() == states.STATE_SHOW_EDIT_SESSION_FORM

    form = sessions_select_screen._widgets_factory.create('create_session_form',
            bad_connection_data['data'])

    sessions_select_screen._state_machine.change_state('save', form)
    assert sessions_select_screen._state_machine.get_current_state() == states.STATE_SHOW_EDIT_SESSION_FORM
    assert form._status_bar.text == bad_connection_data['expected_message']

def test_screen_adds_new_session(empty_registry, good_connection_data):
    sessions_select_screen = session_select.SessionSelect(empty_registry)

    sessions_select_screen._state_machine.change_state('yes')
    assert sessions_select_screen._state_machine.get_current_state() == states.STATE_SHOW_EDIT_SESSION_FORM

    form = sessions_select_screen._widgets_factory.create('create_session_form',
            good_connection_data)

    sessions_select_screen._state_machine.change_state('save', form)
    assert sessions_select_screen._state_machine.get_current_state() == states.STATE_SHOW_SESSIONS_LIST

    assert empty_registry.is_empty() is False

def test_screen_edits_session(registry_with_a_session):
    sessions_select_screen = session_select.SessionSelect(registry_with_a_session)
    assert sessions_select_screen._state_machine.get_current_state() == states.STATE_SHOW_SESSIONS_LIST

    sessions_list_widget = sessions_select_screen.view.original_widget.body

    sessions_select_screen._state_machine.change_state('edit',
            sessions_list_widget, 'Edit')
    assert sessions_select_screen._state_machine.get_current_state() == states.STATE_SHOW_EDIT_SESSION_FORM

    form_data = registry_with_a_session['Test session']
    form_data['name'] = 'Test session'
    form = sessions_select_screen._widgets_factory.create('create_session_form',
            form_data)

    form._input_elements['name'].edit_text = 'Edited session'

    sessions_select_screen._state_machine.change_state('save', form)
    assert sessions_select_screen._state_machine.get_current_state() == states.STATE_SHOW_SESSIONS_LIST
    assert registry_with_a_session.has_session('Edited session')
    assert len(registry_with_a_session.sessions) == 1


def test_screen_deletes_session(registry_with_a_session):
    sessions_select_screen = session_select.SessionSelect(registry_with_a_session)
    assert sessions_select_screen._state_machine.get_current_state() == states.STATE_SHOW_SESSIONS_LIST

    sessions_list_widget = sessions_select_screen.view.original_widget.body

    sessions_select_screen._state_machine.change_state('delete',
            sessions_list_widget, 'delete')
    assert sessions_select_screen._state_machine.get_current_state() == states.STATE_SHOW_CREATE_SESSION_DIALOG
    assert registry_with_a_session.is_empty() is True

def test_screen_shows_form_validation_error_on_edit(registry_with_a_session, bad_connection_data):
    sessions_select_screen = session_select.SessionSelect(registry_with_a_session)
    assert sessions_select_screen._state_machine.get_current_state() == states.STATE_SHOW_SESSIONS_LIST

    sessions_list_widget = sessions_select_screen.view.original_widget.body

    sessions_select_screen._state_machine.change_state('edit',
            sessions_list_widget, 'Edit')
    assert sessions_select_screen._state_machine.get_current_state() == states.STATE_SHOW_EDIT_SESSION_FORM

    form = sessions_select_screen._widgets_factory.create('create_session_form',
            bad_connection_data['data'])

    sessions_select_screen._state_machine.change_state('save', form)
    assert sessions_select_screen._state_machine.get_current_state() == states.STATE_SHOW_EDIT_SESSION_FORM
    assert form._status_bar.text == bad_connection_data['expected_message']
