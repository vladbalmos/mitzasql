from .db.connection_fixture import sakila_connection
from mitzasql.db.model import TableModel
from mitzasql.autocomplete.engine import SQLAutocompleteEngine
import pytest
import pudb

def test(sakila_connection):
    raw_sql = '''
    select actor.actor_id,
    (select * from inventory t where t.
    '''

    model = TableModel(sakila_connection, 'address')
    engine = SQLAutocompleteEngine(model)

    suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    print('\n')
    print(suggestions)

