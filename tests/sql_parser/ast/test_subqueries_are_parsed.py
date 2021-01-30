import pytest
from mitzasql.sql_parser.parser import parse, get_last_parsed_node
from mitzasql.utils import dfs

def test_subquery_col_is_last_node_parsed():
    raw_sql  = '''
    SET @var = (SELECT col
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    last_node = get_last_parsed_node()
    assert last_node is not None
    assert last_node.value == 'col'
