from .db.connection_fixture import sakila_connection
from mitzasql.db.model import TableModel
from mitzasql.autocomplete.engine import SQLAutocompleteEngine
import pytest

def test(sakila_connection):
    raw_sql = 'select actor.actor_id'

    model = TableModel(sakila_connection, 'address')
    engine = SQLAutocompleteEngine(model)

    # suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    print(suggestions)

