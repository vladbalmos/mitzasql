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

def test_expr_operators_precedance():
    raw_sql = '''

col1 OR col2 || col3
col1 XOR col2 AND col3 && col4
not !expr

'''
    ast = parse(raw_sql)
    child_ast = ast[0]

    assert child_ast.type == 'operator'
    assert child_ast.value == 'or'
    assert len(child_ast.children) == 2

    assert child_ast.children[0].value == 'col1'

    assert child_ast.children[1].type == 'operator'
    assert child_ast.children[1].value == '||'

    child_ast = ast[1]

    assert child_ast.type == 'operator'
    assert child_ast.value == 'xor'
    assert len(child_ast.children) == 2

    assert child_ast.children[0].value == 'col1'

    assert child_ast.children[1].type == 'operator'
    assert child_ast.children[1].value == '&&'

    and_op = child_ast.children[1]

    assert and_op.children[0].type == 'operator'
    assert and_op.children[0].value == 'and'
    assert and_op.children[1].value == 'col4'

    child_ast = ast[2]
    assert child_ast.type == 'unary_operator'
    assert child_ast.value == 'not'

    assert child_ast.children[0].type == 'unary_operator'
    assert child_ast.children[0].value == '!'

    child_ast = child_ast.children[0].children[0]
    assert child_ast.type == 'unknown'
    assert child_ast.value == 'expr'

def test_not_operator_precedance():
    raw_sql = '''

NOT 1 + 2 MOD (3 / 4)

'''
    ast = parse(raw_sql)

    ast = ast.pop()

    assert len(ast.children) == 1
    assert ast.type == 'unary_operator'
    assert ast.value == 'not'
