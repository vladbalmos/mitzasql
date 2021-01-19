import pudb
import pytest
from mitzasql.sql_parser.parser import parse

def test_paren_groups_are_parsed():
    raw_sql = '''

(col1, col2, col3)
(1 * 2, FN(call), A BETWEEN (1 + 2) AND 100)

'''
    ast = parse(raw_sql)

    for child_ast in ast:
        assert child_ast.type == 'paren_group'
        assert len(child_ast.children) == 3

    ast = ast.pop()

    assert ast.children[0].type == 'operator'
    assert ast.children[1].type == 'function'
    assert ast.children[2].type == 'operator'

    between_op = ast.children.pop()

    assert between_op.children[1].type == 'range'
    assert between_op.children[1].children[0].type == 'paren_group'

def test_identifier_is_parsed():
    raw_sql = '''

`identifier`,
`another`.`identifier`
`count()`

'''
    ast = parse(raw_sql)

    for ast_child in ast:
        assert ast_child.type == 'identifier'

    assert ast[0].value == '`identifier`'

    assert ast[1].value == '`another`'
    assert len(ast[1].children) == 1
    assert ast[1].children[0].type == 'identifier'
    assert ast[1].children[0].value == '`identifier`'

    assert ast[2].value == '`count()`'


def test_interval_is_parsed():
    raw_sql = '''

INTERVAL '1:1' MINUTE_SECOND
INTERVAL 1 DAY
interval '1.99999' SECOND_MICROSECOND

'''
    ast = parse(raw_sql)

    for child_ast in ast:
        assert child_ast.type == 'interval'
        assert child_ast.value.lower() == 'interval'
        assert len(child_ast.children) == 2
        assert child_ast.children[0].type == 'literal'
        assert child_ast.children[1].type == 'keyword'

def test_match_expr_is_parsed():
    raw_sql = '''

MATCH(col1, col2) AGAINST ("string")
match(col3. col4) AGAINST ((1 * 2))
MATCH(col1) AGAINST ('some other string' IN BOOLEAN MODE)
MATCH(col1) against ('some other string' WITH QUERY EXPANSION)

'''
    ast = parse(raw_sql)

    for child_ast in ast:
        assert child_ast.type == 'match'
        assert child_ast.value.lower() == 'match'
        assert len(child_ast.children) == 2
        assert child_ast.children[0].type == 'paren_group'
        assert child_ast.children[1].type == 'operator'
        assert child_ast.children[1].value.lower() == 'against'

    ast = ast.pop()
    against_op = ast.children.pop()
    modifier_op = against_op.children.pop()

    assert modifier_op.type == 'operator'
    assert modifier_op.value == 'modifier'
    assert len(modifier_op.children) == 3

    for modifier in modifier_op.children:
        assert modifier.type == 'keyword'
        assert len(modifier.value) > 0

def test_function_call_is_parsed():
    raw_sql = '''

SUM(*)
MAX((2 + 4) * 2, SUM(col))
MIN(sum(col), AVG(col2))

'''

    ast = parse(raw_sql)

    expected_fn_names = ['SUM', 'MAX', 'MIN']

    counter = 0
    for ast_child in ast:
        assert ast_child.type == 'function'
        assert ast_child.value == expected_fn_names[counter]
        assert len(ast_child.children) >= 1
        counter += 1

    min_fn_ast = ast.pop()
    assert min_fn_ast.children[0].type == 'function'
    assert min_fn_ast.children[0].value == 'sum'

    assert min_fn_ast.children[1].type == 'function'
    assert min_fn_ast.children[1].value == 'AVG'

def test_row_subquery_is_parsed():
    raw_sql = '''

ROW (a, b)
ROW(a,b)
ROW('some_expression') = 2 ^ 4

'''

    ast = parse(raw_sql)

    assert ast[0].type == 'row_subquery'
    assert ast[1].type == 'row_subquery'
    assert ast[2].type == 'operator'

    assert len(ast[0].children) == 2
    assert len(ast[1].children) == 2
    assert len(ast[2].children) == 2

    assert ast[2].children[0].type == 'row_subquery'
    assert ast[2].children[0].children[0].type == 'literal'
    assert ast[2].children[0].children[0].value == "'some_expression'"

def test_variable_is_parsed():
    raw_sql = '''

@variable, @@GLOBAL, @@SESSION
@`my-var` @'my-var' @"my-var"

'''

    ast = parse(raw_sql)
    for child_ast in ast:
        assert child_ast.type == 'variable'
        assert len(child_ast.value) > 0

def test_param_marker_is_parsed():
    raw_sql = '''

?
FN(?, 'literal')

'''

    ast = parse(raw_sql)

    assert ast[0].type == 'param_marker'
    assert ast[1].children[0].type == 'param_marker'

def test_collate_keyword_is_parsed():
    raw_sql = '''

expr COLLATE utf8
FN(col1 collate latin)

'''

    ast = parse(raw_sql)

    assert ast[0].type == 'operator'
    assert ast[0].value == 'collate'
    assert len(ast[0].children) == 2

    assert ast[0].children[0].type == 'unknown'
    assert ast[0].children[0].value == 'expr'

    assert ast[0].children[1].type == 'collation'
    assert ast[0].children[1].value == 'utf8'

    assert ast[1].children[0].type == 'operator'
    assert ast[1].children[0].value == 'collate'

    collate_op = ast[1].children[0]
    assert collate_op.children[0].type == 'unknown'
    assert collate_op.children[0].value == 'col1'

    assert collate_op.children[1].type == 'collation'
    assert collate_op.children[1].value == 'latin'

def test_case_expression_is_parsed():
    raw_sql = '''

case 1 when 1 then 'one'
when 2 then 'two' else 'more' end

case when 1 > 0 then 'true'
when 1 < 0 then 'true' else 'false' end

'''

    ast = parse(raw_sql)

    child_ast = ast[0]

    assert child_ast.type == 'operator'
    assert child_ast.value == 'case'
    assert len(child_ast.children) == 4

    children = child_ast.children

    assert children[0].type == 'value'
    assert len(children[0].children) == 1
    assert children[0].children[0].type == 'literal'
    assert children[0].children[0].value == '1'

    assert children[1].type == 'operator'
    assert children[1].value == 'when'
    assert len(children[1].children) == 2
    assert children[1].children[0].type == 'literal'
    assert children[1].children[0].value == '1'
    assert children[1].children[1].type == 'literal'
    assert children[1].children[1].value == "'one'"

    assert children[2].type == 'operator'
    assert children[2].value == 'when'
    assert len(children[2].children) == 2
    assert children[2].children[0].type == 'literal'
    assert children[2].children[0].value == '2'
    assert children[2].children[1].type == 'literal'
    assert children[2].children[1].value == "'two'"

    assert children[3].type == 'operator'
    assert children[3].value == 'else'
    assert len(children[3].children) == 1
    assert children[3].children[0].type == 'literal'
    assert children[3].children[0].value == "'more'"

    child_ast = ast[1]

    assert child_ast.type == 'operator'
    assert child_ast.value == 'case'
    assert len(child_ast.children) == 3

    children = child_ast.children

    assert children[0].type == 'operator'
    assert children[0].value == 'when'
    assert len(children[0].children) == 2
    assert children[0].children[0].type == 'operator'
    assert children[0].children[0].value == '>'
    assert children[0].children[1].type == 'literal'
    assert children[0].children[1].value == "'true'"

    assert children[1].type == 'operator'
    assert children[1].value == 'when'
    assert len(children[1].children) == 2
    assert children[1].children[0].type == 'operator'
    assert children[1].children[0].value == '<'
    assert children[1].children[1].type == 'literal'
    assert children[1].children[1].value == "'true'"

    assert children[2].type == 'operator'
    assert children[2].value == 'else'
    assert len(children[2].children) == 1
    assert children[2].children[0].type == 'literal'
    assert children[2].children[0].value == "'false'"

def test_exists_expr_is_parsed():
    raw_sql = '''

exists (select * from table)

'''

    ast = parse(raw_sql)
    ast = ast[0]

    assert ast.type == 'unary_operator'
    assert ast.value == 'exists'
    assert len(ast.children) == 1

    assert ast.children[0].type == 'select'
    assert ast.children[0].value == 'select'

def test_subquery_is_parsed():
    pass
