from ..db.connection_fixture import sakila_connection
from mitzasql.db.model import TableModel
from mitzasql.autocomplete.engine import SQLAutocompleteEngine
import pytest

def test_columns_in_current_table_suggestions(sakila_connection):
    raw_sql = '''
    SELECT 
    '''

    model = TableModel(sakila_connection, 'address')
    engine = SQLAutocompleteEngine(model)

    suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    suggestions = suggestions[0]

    assert len(suggestions) > 0
    assert 'address_id' in suggestions
    assert 'address' in suggestions
    assert 'district' in suggestions

def test_columns_in_table_identifier_suggestions(sakila_connection):
    raw_sql = '''
    SELECT actor.
    '''

    model = TableModel(sakila_connection, 'address')
    engine = SQLAutocompleteEngine(model)

    suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    suggestions = suggestions[0]

    assert len(suggestions) > 0
    assert 'actor_id' in suggestions
    assert 'first_name' in suggestions
    assert 'last_name' in suggestions

def test_columns_in_database_table_identifier_suggestions(sakila_connection):
    raw_sql = '''
    SELECT sakila.actor.
    '''

    model = TableModel(sakila_connection, 'address')
    engine = SQLAutocompleteEngine(model)

    suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    suggestions = suggestions[0]

    assert len(suggestions) > 0
    assert 'actor_id' in suggestions
    assert 'first_name' in suggestions
    assert 'last_name' in suggestions

def test_tables_in_from_clause_suggestions(sakila_connection):
    raw_sql = '''
    SELECT * FROM 
    '''

    model = TableModel(sakila_connection, 'address')
    engine = SQLAutocompleteEngine(model)

    suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    suggestions = suggestions[0]

    assert len(suggestions) > 0
    assert 'actor' in suggestions
    assert 'address' in suggestions

def test_tables_with_db_identifier_in_from_clause_suggestions(sakila_connection):
    raw_sql = '''
    SELECT * FROM sakila.
    '''

    model = TableModel(sakila_connection, 'address')
    engine = SQLAutocompleteEngine(model)

    suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    suggestions = suggestions[0]

    assert len(suggestions) > 0
    assert 'actor' in suggestions
    assert 'address' in suggestions
    assert 'inventory' in suggestions
    assert 'inventory' in suggestions

def test_columns_in_where_suggestions(sakila_connection):
    raw_sql = '''
    SELECT * FROM actor WHERE 
    '''

    model = TableModel(sakila_connection, 'address')
    engine = SQLAutocompleteEngine(model)

    suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    suggestions = suggestions[0]

    assert len(suggestions) > 0
    assert 'actor_id' in suggestions
    assert 'first_name' in suggestions
    assert 'last_name' in suggestions

def test_columns_in_table_alias_in_where_suggestions(sakila_connection):
    raw_sql = '''
    SELECT * FROM actor t1 WHERE t1.
    '''

    model = TableModel(sakila_connection, 'address')
    engine = SQLAutocompleteEngine(model)

    suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    suggestions = suggestions[0]

    assert len(suggestions) > 0
    assert 'actor_id' in suggestions
    assert 'first_name' in suggestions
    assert 'last_name' in suggestions

def test_column_alias_in_order_by_clause_suggestions(sakila_connection):
    raw_sql = '''
    SELECT actor_id aid FROM actor ORDER BY 
    '''

    model = TableModel(sakila_connection, 'address')
    engine = SQLAutocompleteEngine(model)

    suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    suggestions = suggestions[0]

    assert len(suggestions) > 0
    assert 'aid' in suggestions
    assert 'first_name' in suggestions
    assert 'last_name' in suggestions

def test_table_in_join_clause_suggestions(sakila_connection):
    raw_sql = '''
    SELECT actor_id aid FROM actor JOIN 
    '''

    model = TableModel(sakila_connection, 'address')
    engine = SQLAutocompleteEngine(model)

    suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    suggestions = suggestions[0]

    assert len(suggestions) > 0
    assert 'actor_info' in suggestions
    assert 'address' in suggestions

def test_db_table_in_join_clause_suggestions(sakila_connection):
    raw_sql = '''
    SELECT actor_id aid FROM actor JOIN sakila.
    '''

    model = TableModel(sakila_connection, 'address')
    engine = SQLAutocompleteEngine(model)

    suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    suggestions = suggestions[0]

    assert len(suggestions) > 0
    assert 'actor_info' in suggestions
    assert 'address' in suggestions

def test_column_in_join_spec_suggestions(sakila_connection):
    raw_sql = '''
    SELECT actor_id FROM actor ac JOIN actor_info ai ON ai.
    '''

    model = TableModel(sakila_connection, 'address')
    engine = SQLAutocompleteEngine(model)

    suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    suggestions = suggestions[0]

    assert len(suggestions) > 0
    assert 'film_info' in suggestions
    assert 'actor_id' in suggestions

def test_subquery_column_suggestions(sakila_connection):
    raw_sql = '''
    SELECT actor_id, (SELECT * from inventory WHERE 
    '''

    model = TableModel(sakila_connection, 'address')
    engine = SQLAutocompleteEngine(model)

    suggestions = engine.get_suggestions(raw_sql, len(raw_sql))
    suggestions = suggestions[0]

    assert len(suggestions) > 0
    assert 'inventory_id' in suggestions
    assert 'last_update' in suggestions
