from .db.connection_fixture import sakila_connection
from mitzasql.db.model import TableModel
from mitzasql.autocomplete.engine import SQLAutocompleteEngine
import pytest
import pudb

def test(sakila_connection):
    # this query crashes progam when pasting it in the query window
    # raw_sql = '''
    # set @vlad = '1', @razvan = (select id from actor);                                                                                                                     │
    # call film_in_stock(
    # '''

    raw_sql = '''
    set @vlad = '1', @razvan = (select actor
    '''

    model = TableModel(sakila_connection, 'address')
    engine = SQLAutocompleteEngine(model)

    suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    print('\n')
    print(suggestions)

