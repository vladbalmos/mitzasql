import os
import pytest

import urwid
import mysql.connector.errors as errors
from mitzasql.db.model import QueryModel
from .connection_fixture import sakila_connection

def test_model_fetches_data(sakila_connection):
    query = 'SELECT address_id, address, location FROM address LIMIT 10'
    model = QueryModel(sakila_connection, query)
    assert model.last_error is None
    assert len(model) == 10
    assert len(model.columns) == 3
    assert 'address_id' in [c['name'] for c in model.columns]
    assert 'address' in [c['name'] for c in model.columns]
    assert 'location' in [c['name'] for c in model.columns]

def test_model_sets_last_error_when_query_is_invalid(sakila_connection):
    query = 'SELECT unknown_column, address, location FROM address LIMIT 10'
    model = QueryModel(sakila_connection, query)
    assert isinstance(model.last_error, errors.ProgrammingError)
