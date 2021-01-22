from .db.connection_fixture import sakila_connection
from mitzasql.db.model import TableModel
from mitzasql.autocomplete.engine import SQLAutocompleteEngine
import pytest

def test(sakila_connection):
    raw_sql = '''
    select actor_id from actor t1 join actor_info t2 on
        (t1.a = t2.b and sakila.t3.c = 1)
    left join t1 on t1.b = t2.
    '''

    model = TableModel(sakila_connection, 'address')
    engine = SQLAutocompleteEngine(model)

    # suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    print('\n')
    print(suggestions)

