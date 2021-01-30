import pytest
from mitzasql.sql_parser.parser import parse
from mitzasql.utils import dfs

def test_set_single_variable_is_parsed():
    raw_sql  = '''
    SET @v = 1
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'set'
    assert len(ast.children) == 1

    assert ast.children[0].type == 'variable'
    assert len(ast.children[0].children) == 1

    op = ast.children[0].children[0]

    assert op.type == 'operator'
    assert len(op.children) == 2
    assert op.children[0].value == '@v'
    assert op.children[1].value == '1'

def test_set_multiple_variables_is_parsed():
    raw_sql = '''
    SET a := 1, @v = 2, @@v = 3
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'set'
    assert len(ast.children) == 3

    var = ast.children[0]
    assert var.type == 'variable'
    assert len(var.children) == 1

    op = var.children[0]
    assert op.type == 'operator'
    assert len(op.children) == 2

    assert op.children[0].value == 'a'
    assert op.children[1].value == '1'

    var = ast.children[1]
    assert var.type == 'variable'
    assert len(var.children) == 1

    op = var.children[0]
    assert op.type == 'operator'
    assert len(op.children) == 2

    assert op.children[0].value == '@v'
    assert op.children[1].value == '2'

    var = ast.children[2]
    assert var.type == 'variable'
    assert len(var.children) == 1

    op = var.children[0]
    assert op.type == 'operator'
    assert len(op.children) == 2

    assert op.children[0].value == '@@v'
    assert op.children[1].value == '3'

def test_set_variable_modifiers_is_parsed():
    raw_sql  = '''
    SET GLOBAL g = 1, SESSION s = 2, LOCAL l = 3, @var = 1;
    SET @@GLOBAL.g = 1, @@SESSION.s = 2, @@LOCAL.l = 3, @var = 1;
    '''

    ast = parse(raw_sql)
    assert len(ast) == 2

    def test(set_ast):
        assert set_ast.type == 'set'
        assert len(set_ast.children) == 4

        op = set_ast.children[0].children[0]
        assert op.type == 'operator'
        assert len(op.children) == 2
        assert op.children[0].value == '@@GLOBAL.g'

        op = set_ast.children[1].children[0]
        assert op.type == 'operator'
        assert len(op.children) == 2
        assert op.children[0].value == '@@SESSION.s'

        op = set_ast.children[2].children[0]
        assert op.type == 'operator'
        assert len(op.children) == 2
        assert op.children[0].value == '@@LOCAL.l'

        op = set_ast.children[3].children[0]
        assert op.type == 'operator'
        assert len(op.children) == 2
        assert op.children[0].value == '@var'

    test(ast[0])
    test(ast[1])

def test_set_variable_from_subquery():
    raw_sql  = '''
    SET @s :=
        (SELECT col FROM table JOIN table2 ON table.a = table.b),
        LOCAL l = 20
    '''

    ast = parse(raw_sql)
    assert len(ast) > 0

    ast = ast[0]

    assert ast.type == 'set'
    assert len(ast.children) == 2

    assert ast.children[0].type == 'variable'
    assert len(ast.children[0].children) == 1

    op = ast.children[0].children[0]

    assert op.type == 'operator'
    assert len(op.children) == 2
    assert op.children[0].value == '@s'
    assert op.children[1].type == 'select'

    op = ast.children[1].children[0]
    assert op.type == 'operator'
    assert len(op.children) == 2
    assert op.children[0].value == '@@LOCAL.l'
    assert op.children[1].value == '20'
