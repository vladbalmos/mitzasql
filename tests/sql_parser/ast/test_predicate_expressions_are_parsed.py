import pudb
import pytest
from mitzasql.sql_parser.parser import parse
from mitzasql.utils import dfs

def test_between_operator_is_parsed():
    raw_sql = '''

a between 1 and 100
a not between 1 and 100

'''
    ast = parse(raw_sql)

    for child_ast in ast:
        assert child_ast.type == 'operator'
        assert child_ast.value == 'between'
        assert len(child_ast.children) == 2

    child_ast = ast[0]

    assert child_ast.children[0].type == 'unknown'
    assert child_ast.children[0].value == 'a'

    assert child_ast.children[1].type == 'range'

    range = child_ast.children[1]
    assert len(range.children) == 2
    assert range.children[0].type == 'literal'
    assert range.children[0].value == '1'

    assert range.children[1].type == 'literal'
    assert range.children[1].value == '100'

    child_ast = ast[1]

    assert child_ast.children[0].type == 'unknown'
    assert child_ast.children[0].value == 'a'

    assert child_ast.children[1].type == 'operator'
    assert child_ast.children[1].value == 'not'

    assert child_ast.children[1].children[0].type == 'range'
    assert len(child_ast.children[1].children[0].children) == 2

def test_like_operator_is_parsed():
    raw_sql = '''

a like 'something'
a not like '%something%' escape '%'

'''
    ast = parse(raw_sql)

    for child_ast in ast:
        assert child_ast.type == 'operator'
        assert child_ast.value == 'like'
        assert len(child_ast.children) > 1

    assert ast[0].children[0].type == 'unknown'
    assert ast[0].children[0].value == 'a'

    assert ast[0].children[1].type == 'literal'
    assert ast[0].children[1].value == "'something'"

    assert ast[1].children[0].type == 'unknown'
    assert ast[1].children[0].value == 'a'

    assert ast[1].children[1].type == 'operator'
    assert ast[1].children[1].value == "not"

    not_op = ast[1].children[1]

    assert len(not_op.children) == 1
    assert not_op.children[0].type == 'literal'
    assert not_op.children[0].value == "'%something%'"

def test_sounds_like_operator_is_parsed():
    raw_sql = '''

a sounds like 'string'

'''
    ast = parse(raw_sql)
    ast = ast.pop()

    assert ast.type == 'operator'
    assert ast.value == 'sounds'

    assert len(ast.children) == 2

    assert ast.children[0].type == 'unknown'
    assert ast.children[0].value == 'a'

    assert ast.children[1].type == 'operator'
    assert ast.children[1].value == 'like'

    assert ast.children[1].children[0].type == 'literal'
    assert ast.children[1].children[0].value == "'string'"

def test_regexp_operator_is_parsed():
    raw_sql = '''

a regexp 'expr'
a not regexp 'expr'

'''
    ast = parse(raw_sql)

    for child_ast in ast:
        assert child_ast.type == 'operator'
        assert child_ast.value == 'regexp'
        assert len(child_ast.children) == 2

    assert ast[0].children[0].type == 'unknown'
    assert ast[0].children[0].value == 'a'

    assert ast[0].children[1].type == 'literal'
    assert ast[0].children[1].value == "'expr'"

    assert ast[1].children[0].type == 'unknown'
    assert ast[1].children[0].value == 'a'

    assert ast[1].children[1].type == 'operator'
    assert ast[1].children[1].value == "not"

    not_op = ast[1].children[1]

    assert len(not_op.children) == 1

    assert not_op.children[0].type == 'literal'
    assert not_op.children[0].value == "'expr'"

def test_in_paren_expression_is_parsed():
    raw_sql = '''

num in (1, 2, 3)


'''
    ast = parse(raw_sql)
    ast = ast[0]

    assert ast.type == 'operator'
    assert ast.value == 'in'
    assert len(ast.children) == 2

    assert ast.children[0].type == 'unknown'
    assert ast.children[0].value == 'num'

    assert ast.children[1].type == 'paren_group'
    assert len(ast.children[1].children) == 3

def test_in_subquery_expression_is_parsed():
    raw_sql = '''
    num in (SELECT id FROM table)
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0
    ast = ast[0]

    assert ast.type == 'operator'
    assert ast.value == 'in'
    assert len(ast.children) == 2

    assert ast.children[0].type == 'unknown'
    assert ast.children[0].value == 'num'

    assert ast.children[1].type == 'select'
    assert len(ast.children[1].children) == 2
