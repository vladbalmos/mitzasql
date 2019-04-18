import os
import pytest

import urwid
import mysql.connector.errors as errors
from mitzasql.db.model import DBTablesModel
from .connection_fixture import connection

database = 'sakila'

def test_model_fetches_data(connection):
    model = DBTablesModel(connection, database)
    assert len(model) == 35
    assert 'Name' in [c['name'] for c in model.columns]

    table_names = []
    for row in model:
        table_names.append(row[0])

    assert 'actor' in table_names

def test_model_handles_error_if_database_is_invalid(connection):
    model = DBTablesModel(connection, database)

    assert model.last_error is None
    model.database = 'unknown database'
    model.reload()
    assert isinstance(model.last_error, errors.ProgrammingError)

def test_model_emits_signals_during_reloading(connection):
    model = DBTablesModel(connection, database)
    pre_load_signal_handled = False
    load_signal_handled = False

    def pre_load_handler(emitter):
        nonlocal pre_load_signal_handled
        pre_load_signal_handled = True

    def load_handler(emitter):
        nonlocal load_signal_handled
        load_signal_handled = True

    urwid.connect_signal(model, model.SIGNAL_PRE_LOAD, pre_load_handler)
    urwid.connect_signal(model, model.SIGNAL_LOAD, load_handler)

    model.reload()

    assert pre_load_signal_handled is True
    assert load_signal_handled is True

