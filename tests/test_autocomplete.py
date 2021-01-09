from .db.connection_fixture import sakila_connection
from mitzasql.autocomplete.engine import SQLAutocompleteEngine
import pytest

def test(sakila_connection):
    raw_sql = 'select a, b, c where 1'

    engine = SQLAutocompleteEngine(sakila_connection)

    # suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    suggestions = engine.get_suggestions(raw_sql, 17)
    print(suggestions)

