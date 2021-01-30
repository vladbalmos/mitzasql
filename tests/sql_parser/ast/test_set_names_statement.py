import pytest
from mitzasql.sql_parser.parser import parse
from mitzasql.utils import dfs

def test_set_names_is_parsed():
    raw_sql  = '''
    SET names 'utf8';
    set names utf8;
    '''

    ast = parse(raw_sql)
    assert len(ast) == 2

    def test(ast, expected_name):
        assert ast.type == 'set'

        assert len(ast.children) == 1
        assert ast.children[0].type == 'names'

        names = ast.children[0]
        assert len(names.children) == 1

        assert names.children[0].value == expected_name

    test(ast[0], "'utf8'")
    test(ast[1], 'utf8')

def test_set_names_with_collation_is_parsed():
    raw_sql  = '''
    SET names 'utf8' COLLATE 'collation';
    '''

    ast = parse(raw_sql)
    assert len(ast) == 1

    collate_ast = ast[0]
    assert collate_ast.type == 'set'

    assert len(collate_ast.children) == 1
    assert collate_ast.children[0].type == 'names'

    names = collate_ast.children[0]
    assert len(names.children) == 1

    collate_op = names.children[0]
    assert collate_op.type == 'operator'
    assert collate_op.value == 'collate'

    assert len(collate_op.children) == 2
    assert collate_op.children[0].value == "'utf8'"
    assert collate_op.children[1].value == "'collation'"

def test_set_names_with_default_is_parsed():
    raw_sql  = '''
    SET names 'utf8' DEFAULT;
    '''

    ast = parse(raw_sql)
    assert len(ast) == 1

    ast = ast[0]
    assert ast.type == 'set'

    names = ast.children[0]
    assert len(names.children) == 2

    assert names.children[0].value == "'utf8'"
    assert names.children[1].type == 'default'
    assert names.children[1].value == 'DEFAULT'
