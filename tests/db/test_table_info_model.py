import pytest

from mitzasql.db.model import TableInfoModel
from .connection_fixture import sakila_connection

def test_model_fetches_data(sakila_connection):
    model = TableInfoModel(sakila_connection, 'sakila', 'address')

    assert model.last_error is None
    assert isinstance(model.data, dict)

    assert len(model) == 2
    assert model['table']['TABLE_NAME'] == 'address'
    assert model['table']['TABLE_SCHEMA'] == 'sakila'
    assert len(model['create_code']) > 0

def test_model_is_empty(sakila_connection):
    model = TableInfoModel(sakila_connection, 'sakila', 'unknown model')

    assert model.last_error is None
    assert len(model) == 0

def test_model_does_not_raise_exception_on_error(sakila_connection):
    model = TableInfoModel(sakila_connection, 'sakila\' FROM x', 'address')
    assert model.last_error is not None
