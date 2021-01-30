import pytest
from mitzasql.sql_parser.parser import parse
from mitzasql.utils import dfs

def test_simple_update_is_parsed():
    raw_sql  = '''
    UPDATE table1 SET col = 20 WHERE id > 1 ORDER BY id LIMIT 10
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'update'
    assert len(ast.children) == 5

    table_refs = ast.get_child('table_references')
    assert table_refs is not None
    assert len(table_refs.children) == 1

    table_ref = table_refs.children[0]
    assert len(table_ref.children) == 1

    table = table_ref.children[0]
    assert table.value == 'table1'

    assignment_list = ast.get_child('assignment_list')
    assert assignment_list is not None
    assert assignment_list.value == 'SET'

    assert len(assignment_list.children) == 1

    assert assignment_list.children[0].type == 'operator'
    assert assignment_list.children[0].value == '='

    assert ast.get_child('where') is not None
    assert ast.get_child('order') is not None
    assert ast.get_child('limit') is not None

def test_update_with_modifier_is_parsed():
    raw_sql  = '''
    UPDATE low_priority table1 SET col = 20 WHERE id > 1 ORDER BY id LIMIT 10
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'update'
    assert len(ast.children) == 6

    modifier = ast.get_child('modifier')
    assert modifier is not None
    assert len(modifier.children) == 1
    assert modifier.children[0].value == 'low_priority'

    table_refs = ast.get_child('table_references')
    assert table_refs is not None
    assert len(table_refs.children) == 1

    table_ref = table_refs.children[0]
    assert len(table_ref.children) == 1

    table = table_ref.children[0]
    assert table.value == 'table1'

    assignment_list = ast.get_child('assignment_list')
    assert assignment_list is not None
    assert assignment_list.value == 'SET'

    assert len(assignment_list.children) == 1

    assert assignment_list.children[0].type == 'operator'
    assert assignment_list.children[0].value == '='

    assert ast.get_child('where') is not None
    assert ast.get_child('order') is not None
    assert ast.get_child('limit') is not None

def test_update_multiple_tables_stmt_is_parsed():
    raw_sql  = '''
    UPDATE table1, table2 SET col = 20, col1 = (col5 + table2.col4) WHERE id > 1 ORDER BY id LIMIT 10
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'update'
    assert len(ast.children) == 5

    table_refs = ast.get_child('table_references')
    assert table_refs is not None
    assert len(table_refs.children) == 2

    table_ref = table_refs.children[0]
    assert len(table_ref.children) == 1

    table = table_ref.children[0]
    assert table.value == 'table1'

    table_ref = table_refs.children[1]
    assert len(table_ref.children) == 1

    table = table_ref.children[0]
    assert table.value == 'table2'

def test_update_joined_tables_stmt_is_parsed():
    raw_sql  = '''
    UPDATE table1 t1, table2 AS t2 JOIN table3 t3 ON (t1.id = t2.id AND t2.id =
    t3.id)  SET col = 20, col1 = (col5 + table2.col4) WHERE id > 1 ORDER BY id LIMIT 10
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'update'
    assert len(ast.children) == 5

    table_refs = ast.get_child('table_references')
    assert table_refs is not None
    assert len(table_refs.children) == 2

    table_ref = table_refs.children[0]
    assert len(table_ref.children) == 2

    table = table_ref.children[0]
    assert table.value == 'table1'

    table = table_ref.children[1]
    assert table.type == 'alias'

    table_ref = table_refs.children[1]
    assert len(table_ref.children) == 3

    table = table_ref.children[0]
    assert table.value == 'table2'

    table = table_ref.children[1]
    assert table.type == 'alias'

    table = table_ref.children[2]
    assert table.type == 'join'

    assignment_list = ast.get_child('assignment_list')
    assert assignment_list is not None
    assert assignment_list.value == 'SET'

    assert len(assignment_list.children) == 2

    assert assignment_list.children[0].type == 'operator'
    assert assignment_list.children[0].value == '='

    assert ast.get_child('where') is not None
    assert ast.get_child('order') is not None
    assert ast.get_child('limit') is not None

