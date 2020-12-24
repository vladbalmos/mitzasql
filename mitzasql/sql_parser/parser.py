import os
import itertools
from collections import deque
import mitzasql.sql_parser.tokens as Token
import mitzasql.sql_parser.ast as ast
from mitzasql.sql_parser.lexer import Lexer
import pudb

comparison_operators = [
    '=',
    '>=',
    '>',
    '<=',
    '<',
    '<>',
    '!=',
]

valid_boolean_primary_operators = [
    'is',
    '=',
    '<=>',
    '>=',
    '>',
    '<=',
    '<',
    '<>',
    '!=',
]

valid_bit_expr_operators = [
    '^',
    '*',
    '/',
    'div',
    '%',
    'mod',
    '-',
    '+',
    '<<',
    '>>',
    '&',
    '|'
]

tokens = None
t = None

def dfs(root, padding_left=0):
    if not root:
        return

    if padding_left == 0:
        print('\n')

    print(''.rjust(padding_left, ' ') + str(root))

    for child in root.children:
        dfs(child, padding_left + 5)

def token_is_valid_boolean_primary_operator():
    if t is None:
        return False

    if t[0] not in Token.Operator:
        return False

    return t[1] in valid_boolean_primary_operators


def token_is_valid_bit_expr_operator():
    if t is None:
        return False

    if t[0] not in Token.Operator:
        return False

    return t[1] in valid_bit_expr_operators

def skip_whitespace():
    while t is not None and (t[0] == Token.Whitespace or t[0] == Token.Comment):
        next_token()

def next_token():
    global t
    try:
        value = next(tokens)
    except StopIteration:
        value = None
    t = value
    skip_whitespace()

def parse_collation():
    if t is None or t[0] != Token.Other:
        return

    ttype, value = t
    next_token()
    return ast.Expression(value, 'collation')

def parse_expr_term():
    if t is None or t[0] == Token.Comma:
        return

    ttype, value = t

    if ttype in Token.Literal:
        next_token()
        return ast.Expression(value, 'literal')

    if ttype == Token.Name:
        next_token()
        return ast.Expression(value, 'identifier')

    if ttype == Token.Keyword:
        next_token()
        return ast.Expression(value, 'keyword')

    if ttype in Token.Operator:
        if value in ast.unary_operators:
            next_token()
            expr = ast.UnaryOp(value.lower())
            expr.add_child(parse_simple_expr())
            return expr

    if ttype in Token.Reserved:
        if value.lower() == 'binary':
            next_token()
            expr = ast.UnaryOp(value.lower())
            expr.add_child(parse_simple_expr())
            return expr

        if value.lower() == 'interval':
            next_token()
            expr = ast.Expression(value, 'interval')
            expr.add_child(parse_simple_expr())
            expr.add_child(parse_simple_expr())
            return expr

    if ttype == Token.Variable:
        next_token()
        return ast.Expression(value, 'variable')

    if ttype == Token.ParamMarker:
        next_token()
        return ast.Expression(value, 'param_marker')

    if ttype == Token.Other:
        next_token()
        return ast.Expression(value, 'unknown')

def parse_simple_expr():
    expr = parse_expr_term()
    if expr is None:
        return

    if t is None:
        return expr

    ttype, value = t

    if ttype in Token.Operator and value == '||':
        next_token()
        op = ast.Op(value.lower())
        op.add_child(expr)
        op.add_child(parse_simple_expr())
        return op

    if ttype in Token.Reserved:
        if value.lower() == 'collate':
            next_token()
            op = ast.Op(value.lower())
            op.add_child(expr)
            op.add_child(parse_collation())
            return op

    return expr

def parse_bit_expr(prev_operator=None):
    lexpr = parse_simple_expr()
    if not token_is_valid_bit_expr_operator():
        if prev_operator:
            prev_operator.add_child(lexpr)
            return prev_operator
        return lexpr

    ttype, value = t
    next_token()

    operator = ast.Op(value.lower())

    if not prev_operator:
        operator.add_child(lexpr)
        return parse_bit_expr(operator)

    if prev_operator.has_precedance(operator):
        prev_operator.add_child(lexpr)
        operator.add_child(prev_operator)
        return parse_bit_expr(operator)

    operator.add_child(lexpr)
    prev_operator.add_child(parse_bit_expr(operator))
    return prev_operator

def parse_predicate(lexpr = None):
    if lexpr is None:
        lexpr = parse_bit_expr()
        if lexpr is None:
            return

    if t is None:
        return lexpr

    ttype, value = t

    if ttype in Token.Operator:
        lvalue = value.lower()
        if lvalue == 'not':
            next_token()
            op = ast.UnaryOp(lvalue)
            op.add_child(parse_predicate(lexpr))
            return op

        if lvalue == 'sounds':
            next_token()
            op = ast.Op(lvalue)
            op.add_child(lexpr)
            if t is None:
                return op

            if t[0] in Token.Operator and t[1].lower() == 'like':
                next_token()
                like_op = ast.Op(t[1].lower())
                like_op.add_child(parse_bit_expr())
                op.add_child(like_op)

            return op

        if lvalue == 'regexp':
            next_token()
            op = ast.Op(lvalue)
            op.add_child(lexpr)
            op.add_child(parse_bit_expr())
            return op

        if lvalue == 'like':
            next_token()
            op = ast.Op(lvalue)
            op.add_child(lexpr)
            op.add_child(parse_simple_expr())

            if t is None:
                return op

            if t[0] in Token.Keyword and t[1].lower() == 'escape':
                escape_op_value = t[1].lower()
                next_token()
                escape_op = ast.Op(escape_op_value)
                escape_op.add_child(parse_simple_expr())
                op.add_child(escape_op)

            return op

        if lvalue == 'between':
            next_token()
            op = ast.Op(lvalue)
            op.add_child(lexpr)
            op.add_child(parse_bit_expr())

            if t is None:
                return op

            if t[0] in Token.Operator and t[1].lower() == 'and':
                next_token()
                op.add_child(parse_predicate())

            return op

    return lexpr

def parse_boolean_primary():
    # pudb.set_trace()
    lexpr = parse_predicate()
    ttype, value = t
    if lexpr is None:
        return

    if t is None:
        return lexpr

    # print(t)
    if not token_is_valid_boolean_primary_operator():
        return lexpr

    ttype, value = t
    next_token()

    lvalue = value.lower()
    operator = ast.Op(lvalue)
    operator.add_child(lexpr)

    if lvalue == 'is':
        if t[0] in Token.Operator and t[1].lower() == 'not':
            not_op = ast.UnaryOp('not')
            next_token()

            if t[0] in Token.Literal and t[1].lower() == 'null':
                next_token()
                not_op.add_child(ast.Expression('null', 'literal'))

            operator.add_child(not_op)
            return operator

        if t[0] in Token.Literal and t[1].lower() == 'null':
            next_token()
            operator.add_child(ast.Expression('null', 'literal'))
            return operator

        return operator

    if lvalue == '<=>':
        operator.add_child(parse_predicate())
        return operator

    if lvalue in comparison_operators:
        operator.add_child(parse_predicate())
        return operator

    return lexpr

def parse_select_stmt():
    next_token()

def parse_statement():
    ttype, value = t

    if ttype == Token.Reserved:
        if value.lower() == 'select':
            return parse_select_stmt()

    return parse_boolean_primary()

def parse(raw_sql):
    global tokens
    tokens = Lexer(raw_sql).tokenize()
    statements = []

    next_token()
    while t is not None:
        stmt = parse_statement()
        dfs(stmt)
        statements.append(stmt)
    return statements


