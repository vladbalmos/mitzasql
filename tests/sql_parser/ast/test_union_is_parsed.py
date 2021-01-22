import pudb
import pytest
from mitzasql.sql_parser.parser import parse
from mitzasql.utils import dfs

def test_union_is_parsed():
    raw_sql  = '''
    SELECT col1, col2 FROM tbl1
    UNION
    SELECT col1, col2 FROM tbl2
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'operator'
    assert ast.value == 'UNION'

    assert ast.children[0].type == 'select'
    assert ast.children[1].type == 'select'


def test_union_with_parens_is_parsed():
    raw_sql  = '''
    (SELECT col1, col2 FROM tbl1)
    UNION
    (SELECT col1, col2 FROM tbl2)
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'operator'
    assert ast.value == 'UNION'

    assert ast.children[0].type == 'select'
    assert ast.children[1].type == 'select'


def test_multiple_unions_are_parsed():
    raw_sql  = '''
    (SELECT col1, col2 FROM tbl1)
    UNION
    (SELECT col1, col2 FROM tbl2)
    UNION
    SELECT 1
    UNION
    SELECT
        a,
        b,
        c
    FROM tbl1 JOIN tbl2 JOIN tbl3 USING (a,b, c)
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'operator'
    assert ast.value == 'UNION'

    assert ast.children[0].type == 'select'
    assert ast.children[1].type == 'operator'
    assert ast.children[1].value == 'UNION'

    nested_union = ast.children[1]
    assert nested_union.children[0].type == 'select'
    assert nested_union.children[1].type == 'operator'
    assert nested_union.children[1].value == 'UNION'

    nested_union = nested_union.children[1]
    assert nested_union.children[0].type == 'select'
    assert nested_union.children[1].type == 'select'
