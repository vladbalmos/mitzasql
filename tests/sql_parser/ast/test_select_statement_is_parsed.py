import pudb
import pytest
from mitzasql.sql_parser.parser import parse
from mitzasql.utils import dfs

def test_simple_select_stmt_is_parsed():
    raw_sql = '''

    SELECT col1, col2 FROM tbl1

'''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'select'
    assert len(ast.children) == 2

    columns = ast.get_child('columns')
    table = ast.get_child('from')

    assert len(columns.children) == 2
    assert len(table.children) == 1

    col = columns.children[0]
    col = col.get_last_child()
    assert col.value == 'col1'

    col = columns.children[1]
    col = col.get_last_child()
    assert col.value == 'col2'

    table = table.get_last_child()
    assert table.value == 'tbl1'

def test_select_with_col_and_table_alias_is_parsed():
    raw_sql = '''

    SELECT col1 c1, col2 as c2 FROM tbl1 t1,
    tbl2 AS t2

'''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    columns = ast.get_child('columns')
    tables = ast.get_child('from')

    assert len(columns.children) == 2
    assert len(tables.children) == 2

    col = columns.children[0]
    col_ = col.children[0]
    alias = col.get_last_child()
    assert col_.value == 'col1'
    assert alias.value == 'c1'

    col = columns.children[1]
    col_ = col.children[0]
    alias = col.get_last_child()
    assert col_.value == 'col2'
    assert alias.value == 'c2'

    table = tables.children[0]
    tbl_name = table.children[0].get_last_child()
    alias = table.children[1].get_last_child()
    assert tbl_name.value == 'tbl1'
    assert alias.value == 't1'


    table = tables.children[1]
    tbl_name = table.children[0].get_last_child()
    alias = table.children[1].get_last_child()
    assert tbl_name.value == 'tbl2'
    assert alias.value == 't2'

def test_subquery_as_column():
    raw_sql = '''

    SELECT
        col1,
        (SELECT col2 FROM tbl2 LIMIT 1)
    FROM tbl

'''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    columns = ast.get_child('columns')
    tables = ast.get_child('from')

    assert len(columns.children) == 2
    assert len(tables.children) == 1

    col = columns.children[0]
    col_ = col.children[0]
    assert col_.value == 'col1'

    col = columns.children[1]
    col_ = col.children[0]
    assert col_.type == 'select'

def test_subquery_as_table_reference():
    raw_sql = '''

    SELECT
        col1,
        col2
    FROM (
        SELECT col1, col2 FROM tbl
    ) AS t

'''
    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    columns = ast.get_child('columns')
    tables = ast.get_child('from')

    assert len(columns.children) == 2
    assert len(tables.children) == 1

    table = tables.children[0].children[0]
    table = table.children[0]
    assert table.type == 'select'
