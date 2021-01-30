import pytest
from mitzasql.sql_parser.parser import parse
from mitzasql.utils import dfs

def test_compare_subquery():
    raw_sql = '''
    num > (SELECT id FROM table LIMIT 1)
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0
    ast = ast[0]

    assert ast.type == 'operator'
    assert ast.value == '>'
    assert len(ast.children) == 2

    assert ast.children[0].type == 'unknown'
    assert ast.children[0].value == 'num'

    assert ast.children[1].type == 'select'
    assert len(ast.children[1].children) == 3

def test_compare_with_any_in_subquery():
    raw_sql = '''
    num > ANY (SELECT id FROM table LIMIT 1)
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0
    ast = ast[0]

    assert ast.type == 'operator'
    assert ast.value == '>'
    assert len(ast.children) == 2

    assert ast.children[0].type == 'unknown'
    assert ast.children[0].value == 'num'

    assert ast.children[1].type == 'unary_operator'
    assert ast.children[1].value == 'ANY'
    assert ast.children[1].has_children() == 1

    select = ast.children[1].children[0]

    assert select.type == 'select'
    assert len(select.children) == 3

def test_compare_with_all_in_subquery():
    raw_sql = '''
    num > all (SELECT id FROM table LIMIT 1)
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0
    ast = ast[0]

    assert ast.type == 'operator'
    assert ast.value == '>'
    assert len(ast.children) == 2

    assert ast.children[0].type == 'unknown'
    assert ast.children[0].value == 'num'

    assert ast.children[1].type == 'unary_operator'
    assert ast.children[1].value == 'all'
    assert ast.children[1].has_children() == 1

    select = ast.children[1].children[0]

    assert select.type == 'select'
    assert len(select.children) == 3
