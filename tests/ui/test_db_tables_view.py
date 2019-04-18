import pytest
import urwid

from mitzasql.ui.widgets.db_tables_view import DBTablesView
from mitzasql.db.model import DBTablesModel
from ..db.connection_fixture import sakila_connection

def test_keypresses(sakila_connection):
    model = DBTablesModel(sakila_connection, 'sakila')
    view = DBTablesView(model, sakila_connection)

    size = (80, 30)

    emitter = None
    table = None
    def test_table_is_selected(emitter_, table_):
        nonlocal emitter
        nonlocal table
        emitter = emitter_
        table = table_

    urwid.connect_signal(view, view.SIGNAL_ACTION_SELECT_TABLE,
            test_table_is_selected)

    view.keypress(size, 'down')
    view.keypress(size, 'down')
    view.keypress(size, 'down')
    view.keypress(size, 'up')
    view.keypress(size, 'up')
    view.keypress(size, 'up')

    view.keypress(size, 'enter')

    assert isinstance(emitter, DBTablesView)
    assert table is not None
    old_table = table

    view.keypress(size, 'down')
    view.keypress(size, 'enter')

    assert table is not None
    assert table != old_table

    initial_focus = view._table._focused_row_index
    assert initial_focus > 0

    view.keypress(size, 'f5')
    new_focus = view._table._focused_row_index

    assert new_focus == 0

def test_db_tables_view_searches_for_table(sakila_connection):
    model = DBTablesModel(sakila_connection, 'sakila')
    view = DBTablesView(model, sakila_connection)

    size = (80, 30)

    result = view.search_tables('film')
    assert result is not None

    index, row = result
    assert index > 0
    assert 'del_film' in row

    result = view.search_tables('non existent table')
    assert result is None

def test_resizing_column_doesnt_raise_exception(sakila_connection):
    model = DBTablesModel(sakila_connection, 'sakila')
    view = DBTablesView(model, sakila_connection)

    view.resize_tbl_col('engine', 10)
    view.render((80, 30))
