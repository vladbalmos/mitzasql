import pytest

from mitzasql.db.model import ProcedureModel
from .connection_fixture import sakila_connection

def test_model_fetches_data(sakila_connection):
    model = ProcedureModel(sakila_connection, 'sakila', 'rewards_report')

    assert model.last_error is None
    assert isinstance(model.data, dict)

    assert model['ROUTINE_SCHEMA'] == 'sakila'
    assert model['SPECIFIC_NAME'] == 'rewards_report'
    assert model['ROUTINE_TYPE'] == 'PROCEDURE'
    assert len(model['ROUTINE_DEFINITION']) > 0

def test_model_is_empty(sakila_connection):
    model = ProcedureModel(sakila_connection, 'sakila', 'unknown function')

    assert model.last_error is None
    assert len(model) == 0

def test_model_does_not_raise_exception_on_error(sakila_connection):
    model = ProcedureModel(sakila_connection, 'sakila\' FROM x',
            'rewards_report')

    assert model.last_error is not None
