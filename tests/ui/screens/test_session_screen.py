import pytest

from mitzasql.ui.screens.session import (session, states)
from mitzasql.ui.widgets.db_view import DBView
from mitzasql.ui.widgets.db_tables_view import DBTablesView
from mitzasql.ui.widgets.table_view import TableView
from mitzasql.ui.widgets.query_view import QueryView
from ...db.connection_fixture import (connection, sakila_connection)

def test_screen_displays_the_databases_view(connection):
    screen = session.Session(connection)
    assert screen._state_machine.get_current_state() == states.STATE_SHOW_DATABASES
    assert isinstance(screen.focused_widget, DBView)

def test_screen_transitions_from_database_view_to_db_tables_view(connection):
    screen = session.Session(connection)
    assert screen._state_machine.get_current_state() == states.STATE_SHOW_DATABASES
    screen._state_machine.change_state('select', None, 'sakila')
    assert screen._state_machine.get_current_state() == states.STATE_SHOW_DB_TABLES
    assert isinstance(screen.focused_widget, DBTablesView)

def test_screens_displays_the_db_tables_view(sakila_connection):
    screen = session.Session(sakila_connection)
    assert screen._state_machine.get_current_state() == states.STATE_SHOW_DB_TABLES
    assert isinstance(screen.focused_widget, DBTablesView)

def test_screen_transitions_to_table_view(sakila_connection):
    screen = session.Session(sakila_connection)
    assert screen._state_machine.get_current_state() == states.STATE_SHOW_DB_TABLES
    screen._state_machine.change_state('select', None, 'actor')
    assert screen._state_machine.get_current_state() == states.STATE_SHOW_TABLE
    assert isinstance(screen.focused_widget, TableView)

def test_screen_transitions_to_query_view(sakila_connection):
    screen = session.Session(sakila_connection)
    assert screen._state_machine.get_current_state() == states.STATE_SHOW_DB_TABLES
    screen._state_machine.change_state('run_query', None, 'SELECT COUNT(*) FROM actor')
    assert screen._state_machine.get_current_state() == states.STATE_SHOW_QUERY_TABLE
    assert isinstance(screen.focused_widget, QueryView)

def test_screen_transitions_from_query_view_to_database_view(connection):
    connection.database = None
    screen = session.Session(connection)
    assert isinstance(screen.focused_widget, DBView)
    screen._state_machine.change_state('select', None, 'sakila')
    assert isinstance(screen.focused_widget, DBTablesView)
    screen._state_machine.change_state('select', None, 'actor')
    assert isinstance(screen.focused_widget, TableView)
    screen._state_machine.change_state('run_query', None, 'SELECT COUNT(*) FROM actor')
    assert isinstance(screen.focused_widget, QueryView)
    screen._state_machine.change_state('back', screen)
    assert screen._state_machine.get_current_state() == states.STATE_SHOW_TABLE
    assert isinstance(screen.focused_widget, TableView)
    screen._state_machine.change_state('back', screen)
    assert screen._state_machine.get_current_state() == states.STATE_SHOW_DB_TABLES
    assert isinstance(screen.focused_widget, DBTablesView)
    screen._state_machine.change_state('back', screen)
    assert screen._state_machine.get_current_state() == states.STATE_SHOW_DATABASES
    assert isinstance(screen.focused_widget, DBView)

def test_screen_shows_sql_error(sakila_connection):
    screen = session.Session(sakila_connection)
    screen._state_machine.change_state('run_query', None, 'INVALID SQL')
    assert screen.view.showing_error_modal is True
