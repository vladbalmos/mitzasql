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
    assert table.type == 'select'

def test_inner_join_is_parsed():
    raw_sql = '''
    SELECT
        a,
        b,
        c
    FROM t1 INNER JOIN t2 t on t1.a = t.id
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    from_node = ast.get_child('from')

    assert from_node is not None
    assert len(from_node.children) == 1

    join_type = from_node.get_child('join_type')

    assert join_type is not None
    assert join_type.value == 'INNER'
    assert len(join_type.children) == 1
    assert join_type.children[0].type == 'join'

def test_cross_join_is_parsed():
    raw_sql = '''
    SELECT
        a,
        b,
        c
    FROM t1 CROSS JOIN t2 t on t1.a = t.id
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    from_node = ast.get_child('from')

    assert from_node is not None
    assert len(from_node.children) == 1

    join_type = from_node.get_child('join_type')

    assert join_type is not None
    assert join_type.value == 'CROSS'
    assert len(join_type.children) == 1
    assert join_type.children[0].type == 'join'

def test_straight_join_is_parsed():
    raw_sql = '''
    SELECT
        a,
        b,
        c
    FROM t1 straight_join t2 t on t1.a = t.id
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    from_node = ast.get_child('from')

    assert from_node is not None
    assert len(from_node.children) == 1

    join = from_node.get_child('join')

    assert join is not None
    assert join.value == 'straight_join'

def test_left_join_is_parsed():
    raw_sql = '''
    SELECT
        a,
        b,
        c
    FROM t1 LEFT JOIN t2 t on t1.a = t.id
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    from_node = ast.get_child('from')

    assert from_node is not None
    assert len(from_node.children) == 1

    join_dir = from_node.get_child('join_dir')

    assert join_dir is not None
    assert join_dir.value == 'LEFT'
    assert len(join_dir.children) == 1
    assert join_dir.children[0].type == 'join'

def test_right_outer_join_is_parsed():
    raw_sql = '''
    SELECT
        a,
        b,
        c
    FROM t1 RIGHT OUTER JOIN t2 t on t1.a = t.id
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    from_node = ast.get_child('from')

    assert from_node is not None
    assert len(from_node.children) == 1

    join_dir = from_node.get_child('join_dir')

    assert join_dir is not None
    assert join_dir.value == 'RIGHT'
    assert len(join_dir.children) == 1

    join_type = join_dir.children[0]
    assert join_type is not None
    assert join_type.value == 'OUTER'
    assert len(join_type.children) == 1
    assert join_type.children[0].type == 'join'

def test_natural_right_outer_join_is_parsed():
    raw_sql = '''
    SELECT
        a,
        b,
        c
    FROM t1 NATURAL RIGHT OUTER JOIN t2 t on t1.a = t.id
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    from_node = ast.get_child('from')

    assert from_node is not None
    assert len(from_node.children) == 1

    join_type = from_node.get_child('join_type')

    assert join_type is not None
    assert join_type.value == 'NATURAL'
    assert len(join_type.children) == 1

    join_dir = join_type.get_child('join_dir')

    assert join_dir is not None
    assert join_dir.value == 'RIGHT'
    assert len(join_dir.children) == 1

    join_type = join_dir.children[0]
    assert join_type is not None
    assert join_type.value == 'OUTER'
    assert len(join_type.children) == 1
    assert join_type.children[0].type == 'join'

def test_natural_join_is_parsed():
    raw_sql = '''
    SELECT
        a,
        b,
        c
    FROM t1 NATURAL JOIN t2 t on t1.a = t.id
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    from_node = ast.get_child('from')

    assert from_node is not None
    assert len(from_node.children) == 1

    join_type = from_node.get_child('join_type')

    assert join_type is not None
    assert join_type.value == 'NATURAL'
    assert len(join_type.children) == 1
    assert join_type.children[0].type == 'join'

def test_join_is_parsed():
    raw_sql = '''
    SELECT
        a,
        b,
        c
    FROM t1 JOIN t2 t on t1.a = t.id
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    from_node = ast.get_child('from')

    assert from_node is not None
    assert len(from_node.children) == 1

    table_reference = from_node.children[0]
    assert len(table_reference.children) == 2

    assert table_reference.children[0].type == 'unknown'
    assert table_reference.children[0].value == 't1'

    join = table_reference.children[1]
    assert join is not None
    assert join.value == 'JOIN'

    joined_table = join.get_child('table_reference')
    assert joined_table is not None
    assert len(joined_table.children) == 2

    assert joined_table.children[0].value == 't2'
    assert joined_table.children[1].type == 'alias'

    alias = joined_table.children[1].children[0]
    assert alias.value == 't'

    join_spec = join.get_child('join_spec')
    assert join_spec is not None

    assert len(join_spec.children) == 1
    assert join_spec.children[0].type == 'operator'
    assert join_spec.children[0].value == '='

def test_multiple_join_single_join_spec_is_parsed():
    raw_sql = '''
    SELECT
        a,
        b,
        c
    FROM t1 LEFT JOIN t2
    RIGHT JOIN t3
    NATURAL LEFT OUTER JOIN t4
    ON (t1.a = t2.c AND t2.c = t3.d and t3.e = t4.e)
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    from_node = ast.get_child('from')

    assert from_node is not None
    assert len(from_node.children) == 1

    join_spec = from_node.get_child('join_spec')

    assert join_spec is not None
    assert len(join_spec.children) == 1
    assert join_spec.children[0]
