import pudb
import pytest
from mitzasql.sql_parser.parser import parse
from mitzasql.utils import dfs

def test_do_statement_is_parsed():
    raw_sql  = '''
    do 1 + 1, sleep(5)
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'do'
    assert len(ast.children) == 2

    assert ast.children[0].type == 'operator'
    assert ast.children[1].type == 'function'
