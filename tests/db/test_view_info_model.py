import pytest

from mitzasql.db.model import ViewInfoModel
from .connection_fixture import sakila_connection

def test_model_fetches_data(sakila_connection):
    model = ViewInfoModel(sakila_connection, 'sakila', 'customer_list')

    assert model.last_error is None
    assert isinstance(model.data, dict)

    assert len(model) > 0
    assert model['TABLE_SCHEMA'] == 'sakila'
    assert model['TABLE_NAME'] == 'customer_list'
    assert len(model['VIEW_DEFINITION']) > 0

def test_model_is_empty(sakila_connection):
    model = ViewInfoModel(sakila_connection, 'sakila', 'unknown view')

    assert model.last_error is None
    assert len(model) == 0

def test_model_does_not_raise_exception_on_error(sakila_connection):
    model = ViewInfoModel(sakila_connection, 'sakila\' FROM x', 'customer_create_date')

    assert model.last_error is not None
