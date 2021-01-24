import pudb
import pytest
from mitzasql.sql_parser.parser import parse
from mitzasql.utils import dfs

def test_set_charset_default():
    raw_sql  = '''
    set charset default
    '''

    ast = parse(raw_sql)
    assert len(ast) == 1

    ast = ast[0]

    assert ast.type == 'set'
    assert len(ast.children) == 1
    assert ast.children[0].type == 'charset'

    charset = ast.children[0]
    assert len(charset.children) == 1
    assert charset.children[0].value == 'default'

def test_set_charset_utf8():
    raw_sql  = '''
    set charset utf8
    '''

    ast = parse(raw_sql)
    assert len(ast) == 1

    ast = ast[0]

    assert ast.type == 'set'
    assert len(ast.children) == 1
    assert ast.children[0].type == 'charset'

    charset = ast.children[0]
    assert len(charset.children) == 1
    assert charset.children[0].value == 'utf8'

def test_set_character_set_utf8():
    raw_sql  = '''
    set character set utf8
    '''

    ast = parse(raw_sql)
    assert len(ast) == 1

    ast = ast[0]

    assert ast.type == 'set'
    assert len(ast.children) == 1
    assert ast.children[0].type == 'character'

    character = ast.children[0]
    assert len(character.children) == 1

    set = character.children[0]
    assert set.type == 'set'
    assert len(set.children) == 1
    assert set.children[0].value == 'utf8'
