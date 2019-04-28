import pytest

from mitzasql.db.model import TriggerModel
from .connection_fixture import sakila_connection

def test_model_fetches_data(sakila_connection):
    model = TriggerModel(sakila_connection, 'sakila', 'customer_create_date')

    assert model.last_error is None
    assert isinstance(model.data, dict)

    assert model['TRIGGER_SCHEMA'] == 'sakila'
    assert model['TRIGGER_NAME'] == 'customer_create_date'
    assert model['EVENT_MANIPULATION'] == 'INSERT'
    assert model['EVENT_OBJECT_TABLE'] == 'customer'
    assert len(model['ACTION_STATEMENT']) > 0

def test_model_is_empty(sakila_connection):
    model = TriggerModel(sakila_connection, 'sakila', 'unknown trigger')

    assert model.last_error is None
    assert len(model) == 0

def test_model_does_not_raise_exception_on_error(sakila_connection):
    model = TriggerModel(sakila_connection, 'sakila\' FROM x', 'customer_create_date')

    assert model.last_error is not None
