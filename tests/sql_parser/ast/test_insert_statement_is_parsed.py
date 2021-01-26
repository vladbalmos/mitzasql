import pudb
import pytest
from mitzasql.sql_parser.parser import parse
from mitzasql.utils import dfs

def test_simple_insert_is_parsed():
    raw_sql  = '''
    INSERT DELAYED INTO table (col1, col2, col3) VALUES (100, 200, 300)
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'insert'
    assert len(ast.children) == 4

    modifier = ast.get_child('modifier')
    assert modifier is not None
    assert len(modifier.children) == 1

    into = ast.get_child('into')
    assert into is not None
    assert len(into.children) == 1
    assert into.children[0].children[0].value == 'table'

    columns = ast.get_child('columns')
    assert columns is not None
    assert len(columns.children) == 1
    assert len(columns.children[0].children) == 3

    values = ast.get_child('values')
    assert values is not None
    assert len(values.children) == 1
    assert len(values.children[0].children) == 3

def test_insert_without_columns_is_parsed():
    raw_sql  = '''
    INSERT INTO table VALUES (100, 200, 300)
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'insert'
    assert len(ast.children) == 2

    into = ast.get_child('into')
    assert into is not None
    assert len(into.children) == 1
    assert into.children[0].children[0].value == 'table'

    values = ast.get_child('values')
    assert values is not None
    assert len(values.children) == 1
    assert len(values.children[0].children) == 3

def test_insert_with_select_is_parsed():
    raw_sql  = '''
    INSERT INTO table SELECT col1, col2 FROM tbl2 WHERE col1 > 1 ON DUPLICATE
    KEY UPDATE id = 1
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'insert'
    assert len(ast.children) == 3

    into = ast.get_child('into')
    assert into is not None
    assert len(into.children) == 1
    assert into.children[0].children[0].value == 'table'

    select = ast.get_child('select')
    assert select is not None

    on = ast.get_child('on')
    assert on is not None
    assert len(on.children) == 1

    duplicate = ast.get_child('duplicate')
    assert duplicate is not None
    assert len(duplicate.children) == 1

    key = ast.get_child('key')
    assert key is not None
    assert len(key.children) == 1

    update = ast.get_child('update')
    assert update is not None
    assert len(update.children) == 1

def test_insert_with_assignment_list_is_parsed():
    raw_sql  = '''
    INSERT INTO table SET col1 = 2, col2 = 3
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'insert'
    assert len(ast.children) == 2

    into = ast.get_child('into')
    assert into is not None
    assert len(into.children) == 1
    assert into.children[0].children[0].value == 'table'

    assignment_list = ast.get_child('assignment_list')
    assert assignment_list is not None
    assert len(assignment_list.children) == 2

    assignment = assignment_list.children[0]
    assert assignment.type == 'operator'
    assert assignment.value == '='
    assert len(assignment.children) == 2
    assert assignment.children[0].value == 'col1'
    assert assignment.children[1].value == '2'

    assignment = assignment_list.children[1]
    assert assignment.type == 'operator'
    assert assignment.value == '='
    assert len(assignment.children) == 2
    assert assignment.children[0].value == 'col2'
    assert assignment.children[1].value == '3'
