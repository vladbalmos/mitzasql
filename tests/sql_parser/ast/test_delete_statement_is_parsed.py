import pudb
import pytest
from mitzasql.sql_parser.parser import parse
from mitzasql.utils import dfs

def test_simple_delete_is_parsed():
    raw_sql  = '''
    DELETE FROM table1 WHERE id > 1 ORDER BY id LIMIT 10
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'delete'
    assert len(ast.children) == 4

    table_refs = ast.get_child('from')
    assert table_refs is not None
    assert len(table_refs.children) == 1

    table_ref = table_refs.children[0]
    assert len(table_ref.children) == 1

    table = table_ref.children[0]
    assert table.value == 'table1'

    assert ast.get_child('where') is not None
    assert ast.get_child('order') is not None
    assert ast.get_child('limit') is not None

def test_delete_from_partition_is_parsed():
    raw_sql  = '''
    DELETE FROM table1 PARTITION (p1, p2) WHERE id > 1 ORDER BY id LIMIT 10
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'delete'
    assert len(ast.children) == 4

    table_refs = ast.get_child('from')
    assert table_refs is not None
    assert len(table_refs.children) == 1

    table_ref = table_refs.children[0]
    assert len(table_ref.children) == 2

    table = table_ref.children[0]
    assert table.value == 'table1'

    partition = table_ref.children[1]
    assert partition.type == 'partition'
    assert len(partition.children) == 1
    assert partition.children[0].type == 'paren_group'
    assert len(partition.children[0].children) == 2

    assert ast.get_child('where') is not None
    assert ast.get_child('order') is not None
    assert ast.get_child('limit') is not None

def test_delete_from_multiple_tables():
    raw_sql  = '''
    DELETE FROM table1, table2 WHERE id > 1 ORDER BY id LIMIT 10
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'delete'
    assert len(ast.children) == 4

    table_refs = ast.get_child('from')
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

    assert ast.get_child('where') is not None
    assert ast.get_child('order') is not None
    assert ast.get_child('limit') is not None

def test_delete_using_is_parsed():
    raw_sql  = '''
    DELETE t1.*, t2.* FROM table1 USING t1 JOIN t2 WHERE id > 1 ORDER BY id LIMIT 10
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'delete'
    assert len(ast.children) == 6

    table_refs = ast.get_child('table_references')
    assert table_refs is not None
    assert len(table_refs.children) == 2

    table_ref = table_refs.children[0]
    assert len(table_ref.children) == 1

    table = table_ref.children[0]
    assert table.value == 't1'

    table_ref = table_refs.children[1]
    assert len(table_ref.children) == 1

    table = table_ref.children[0]
    assert table.value == 't2'

    from_ = ast.get_child('from')
    assert from_ is not None
    assert len(from_.children) == 1

    table_ref = from_.children[0]
    assert len(table_ref.children) == 1

    table = table_ref.children[0]
    assert table.value == 'table1'

    using = ast.get_child('using')
    assert len(using.children) == 1

    table_ref = using.children[0]
    assert len(table_ref.children) == 2

    assert table_ref.children[0].value == 't1'
    assert table_ref.children[1].type == 'join'

    assert ast.get_child('where') is not None
    assert ast.get_child('order') is not None
    assert ast.get_child('limit') is not None
