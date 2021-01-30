import pytest
from mitzasql.sql_parser.parser import parse
from mitzasql.utils import dfs

def test_call_statement_with_params_is_parsed():
    raw_sql  = '''
    call p(@v1, 2)
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'call'
    assert len(ast.children) == 1

    assert ast.children[0].type == 'proc'
    assert len(ast.children[0].children) == 1

    fn = ast.children[0].children[0]
    assert len(fn.children) == 2
    assert fn.children[0].value == '@v1'
    assert fn.children[1].value == '2'

def test_call_statement_without_params_is_parsed():
    raw_sql  = '''
    call p
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'call'
    assert len(ast.children) == 1

    assert ast.children[0].type == 'proc'
    assert len(ast.children[0].children) == 1

    fn = ast.children[0].children[0]
    assert fn.value == 'p'
