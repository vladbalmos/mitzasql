import pytest

import urwid
from mitzasql.db.model import DatabasesModel
from .connection_fixture import connection

def test_model_fetches_data(connection):
    model = DatabasesModel(connection)
    assert len(model) > 0
    assert 'Database' in [c['name'] for c in model.columns]

    model_was_iterated = False
    rows = []
    for row in model:
        rows.append(row[0])
        model_was_iterated = True

    assert 'sakila' in rows
    assert len(model.columns)

def test_model_searches_for_sakila(connection):
    model = DatabasesModel(connection)

    result = model.search('saki', 0)
    assert result is not None

    row_index, row = result
    assert row_index > 0
    assert row == ('sakila', )
