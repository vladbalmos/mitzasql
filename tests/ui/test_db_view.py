import pytest
import urwid

from mitzasql.ui.widgets.db_view import DBView
from mitzasql.db.model import DatabasesModel
from ..db.connection_fixture import connection

def test_keypresses(connection):
    model = DatabasesModel(connection)
    view = DBView(model, connection)

    size = (80, 30)

    emitter = None
    database = None
    def test_db_is_selected(emitter_, database_):
        nonlocal emitter
        nonlocal database
        emitter = emitter_
        database = database_

    urwid.connect_signal(view, view.SIGNAL_ACTION_SELECT_DB,
            test_db_is_selected)

    view.keypress(size, 'down')
    view.keypress(size, 'down')
    view.keypress(size, 'down')
    view.keypress(size, 'up')
    view.keypress(size, 'up')
    view.keypress(size, 'up')

    view.keypress(size, 'enter')

    assert isinstance(emitter, DBView)
    assert database is not None
    old_database = database

    view.keypress(size, 'down')
    view.keypress(size, 'enter')
    assert database is not None
    assert database != old_database


def test_db_view_searches_for_database(connection):
    model = DatabasesModel(connection)
    view = DBView(model, connection)

    size = (80, 30)

    result = view.search_db('sakila')
    assert result is not None

    index, row = result
    assert index > 0
    assert 'sakila' in row

    result = view.search_db('non existent database')
    assert result is None

def test_db_view_refreshes_table(connection):
    model = DatabasesModel(connection)
    view = DBView(model, connection)
    size = (80, 30)

    initial_focus = view._table._focused_row_index

    view.keypress(size, 'down')
    view.keypress(size, 'down')

    new_focus = view._table._focused_row_index

    assert new_focus > initial_focus

    model.reload()
    new_focus = view._table._focused_row_index
    assert new_focus == initial_focus
