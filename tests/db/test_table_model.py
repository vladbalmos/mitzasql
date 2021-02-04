import os
import pytest

import mysql.connector.errors as errors
from mitzasql.db.model import TableModel
from .connection_fixture import sakila_connection
from .connection_fixture import connection
from .connection_fixture import db_dash_in_name_connection

table = 'actor'

where_clauses = [
        'address_id = 1',
        'address_id = "1"',
        'address_id != 1',
        'address_id < 1',
        'address_id <= 1',
        'address_id > 1',
        'address_id >= 1',
        'address_id is null',
        'address_id is not null',
        'address_id = ""',
        'address_id != ""',
        'address_id in (1, 2)',
        'address_id not in (1, 2)',
        'address_id between 1 and 10',
        'address_id not between 1 and 10',
        'address like "%hanoi%"',
        'address not like "%hanoi%"',
        ]

@pytest.fixture(params=where_clauses)
def filter(request):
    return request.param

def test_model_fetches_data(sakila_connection):
    model = TableModel(sakila_connection, table)
    model_columns = [c['name'] for c in model.columns]
    assert len(model) == 200
    assert 'actor_id' in model_columns
    assert 'first_name' in model_columns
    assert 'last_name' in model_columns
    assert 'last_update' in model_columns

    assert model.loaded_rowcount == 100

def test_model_fetches_next_records_set(sakila_connection):
    model = TableModel(sakila_connection, table)

    assert model.loaded_rowcount == 100
    model.load_next_set()
    assert model.loaded_rowcount == 200
    assert len(model) == 200

def test_model_loads_more_rows(sakila_connection):
    model = TableModel(sakila_connection, table)

    assert model.loaded_rowcount == 100
    model.load_more(50)
    assert model.loaded_rowcount == 200
    assert len(model) == 200

def test_model_sorts_rows_by_first_name_ascending(sakila_connection):
    model = TableModel(sakila_connection, table)
    model.sort('first_name', 'asc')

    row = model[0]
    assert row[1] == 'ADAM'

def test_model_sorts_rows_by_first_name_descending(sakila_connection):
    model = TableModel(sakila_connection, table)
    model.sort('first_name', 'desc')

    row = model[0]
    assert row[0] == 11
    assert row[1] == 'ZERO'

def test_model_sets_last_error_when_table_doesnt_exist(sakila_connection):
    model = TableModel(sakila_connection, 'unknown table')
    assert isinstance(model.last_error, errors.ProgrammingError)

    assert len(model) == 0
    assert len(model.data) == 0
    assert model.loaded_rowcount == 0
    assert bool(model.columns) is False

def test_model_emits_error_signal(sakila_connection):
    model = TableModel(sakila_connection, table)
    assert model.last_error is None
    model.sort('non-existent-column', 'invalid-dir')
    assert isinstance(model.last_error, errors.ProgrammingError)

    assert len(model) == 0
    assert len(model.data) == 0
    assert model.loaded_rowcount == 0
    assert bool(model.columns) is False

def test_model_filters_records(sakila_connection, filter):
    model = TableModel(sakila_connection, 'address')
    model.filter(filter)

    assert model.last_error is None

def test_model_properly_escapes_dash_in_table_names(db_dash_in_name_connection):
    model = TableModel(db_dash_in_name_connection, 'table-with-dash')
    assert model.last_error is None

def test_model_properly_escapes_alias(sakila_connection):
    long_str = "x" * 1024
    create_table_sql = '''
CREATE TABLE IF NOT EXISTS `table_with_space_in_column_names` (
counter INT NULL,
`column varchar` VARCHAR (1024) NULL,
`column text` TEXT NULL
)
    '''

    sakila_connection.query(create_table_sql)
    sakila_connection.query('''REPLACE INTO table_with_space_in_column_names
            (counter, `column varchar`, `column text`) VALUES (1, "{0}", "{1}" )'''.format(long_str, long_str))

    model = TableModel(sakila_connection, 'table_with_space_in_column_names')
    assert model.last_error is None


