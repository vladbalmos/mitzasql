import pytest
from mitzasql.sql_parser.parser import parse

def test_binary_unary_operator_has_precedance():
    raw_sql = '''
binary 1 * 20
'''
    ast = parse(raw_sql)
    ast = ast[0]

    assert ast.type == 'operator'
    assert ast.value == '*'
    assert len(ast.children) == 2

    ast = ast.children[0]
    assert ast.type == 'unary_operator'
    assert ast.value == 'binary'
    assert len(ast.children) == 1

    ast = ast.children[0]
    assert ast.type == 'literal'
    assert ast.value == '1'

def test_bang_unary_operator_has_precedance():
    raw_sql = '''
!1 + 1
'''
    ast = parse(raw_sql)
    ast = ast[0]

    assert ast.type == 'operator'
    assert ast.value == '+'
    assert len(ast.children) == 2

    last = ast.children[0]
    assert last.type == 'unary_operator'
    assert last.value == '!'
    assert len(last.children) == 1

    assert last.children[0].type == 'literal'
    assert last.children[0].value == '1'

    rast = ast.children[1]
    assert rast.type == 'literal'
    assert rast.value == '1'

def test_mul_div_operators_have_precedance():
    raw_sql = '''
1 * 2 + 9 / 3
'''
    ast = parse(raw_sql)
    ast = ast[0]

    assert ast.type == 'operator'
    assert ast.value == '+'
    assert len(ast.children) == 2

    assert ast.children[0].type == 'operator'
    assert ast.children[0].value == '*'

    assert ast.children[1].type == 'operator'
    assert ast.children[1].value == '/'

def test_add_sub_operators_precedance():
    raw_sql = '''
1 + 2 + 10 - 3
'''
    ast = parse(raw_sql)
    ast = ast[0]

    assert ast.type == 'operator'
    assert ast.value == '-'
    assert len(ast.children) == 2

    last = ast.children[0]
    rast = ast.children[1]

    assert rast.type == 'literal'
    assert rast.value == '3'

    assert last.type == 'operator'
    assert last.value == '+'
    assert len(last.children) == 2

    rast = last.children[1]
    last = last.children[0]

    assert rast.type == 'literal'
    assert rast.value == '10'

    assert last.type == 'operator'
    assert last.value == '+'
    assert len(last.children) == 2

    rast = last.children[1]
    last = last.children[0]

    assert last.type == 'literal'
    assert last.value == '1'

    assert rast.type == 'literal'
    assert rast.value == '2'

def test_parens_hae_precendance():
    raw_sql = '''
(-1 * (2 + 3)) MOD 3
'''
    ast = parse(raw_sql)
    ast = ast[0]

    assert ast.type == 'operator'
    assert ast.value == 'mod'
    assert len(ast.children) == 2

    last = ast.children[0]
    rast = ast.children[1]

    assert rast.type == 'literal'
    assert rast.value == '3'

    assert last.type == 'paren_group'
    assert len(last.children) == 1

    ast = last.children[0]
    assert ast.type == 'operator'
    assert ast.value == '*'
    assert len(ast.children) == 2

    last = ast.children[0]
    rast = ast.children[1]

    assert rast.type == 'paren_group'
    assert rast.children[0].type == 'operator'

