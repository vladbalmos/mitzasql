from collections import deque
import mitzasql.sql_parser.tokens as Token
import mitzasql.sql_parser.ast as ast
from mitzasql.sql_parser.lexer import Lexer
import pudb

visited_tokens_queue = deque()
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

def is_literal(label=None, lowercase=True):
    if t is None:
        return False

    if label is None:
        return t[0] in Token.Literal

    if lowercase is True:
        value = t[1].lower()
    else:
        value = t[1]

    return t[0] in Token.Literal and value == label

def is_operator(label=None):
    if t is None:
        return False

    if label is None:
        return t[0] in Token.Operator

    return t[0] in Token.Operator and t[1].lower() == label.lower()

def skip_past_whitespace():
    while t is not None and (t[0] == Token.Whitespace or t[0] == Token.Comment):
        next_token()

def next_token(skip_whitespace=True):
    global t

    # dequeue any already inspected tokens
    # before advancing to the unprocessed tokens
    if len(visited_tokens_queue):
        t = visited_tokens_queue.popleft()
        return

    try:
        value = next(tokens)
    except StopIteration:
        value = None
    t = value

    if skip_whitespace:
        skip_past_whitespace()


def token_is_valid_expression_operator():
    global visited_tokens_queue
    global t

    if not is_operator():
        return False

    if t[1].lower() not in ast.valid_expression_operators:
        return False

    if not is_operator('is'):
        return True

    return_value = False
    visited_tokens = []
    current_token = t
    next_token()
    visited_tokens.append(t)

    if is_operator('not'):
        next_token()
        visited_tokens.append(t)

    if t and t[1].lower() in ['true', 'false', 'unknown']:
        return_value = True

    for vt in visited_tokens:
        visited_tokens_queue.append(vt)

    t = current_token
    return return_value


def token_is_valid_boolean_primary_operator():
    global visited_tokens_queue
    global t

    if not is_operator():
        return False

    if t[1].lower() not in ast.valid_boolean_primary_operators:
        return False

    if not is_operator('is'):
        return True

    return_value = False
    visited_tokens = []
    current_token = t
    next_token()
    visited_tokens.append(t)

    if is_operator('not'):
        next_token()
        visited_tokens.append(t)

    if t and t[1].lower() == 'null':
        return_value = True

    for vt in visited_tokens:
        visited_tokens_queue.append(vt)

    t = current_token
    return return_value

def token_is_valid_bit_expr_operator():
    if not is_operator():
        return False

    return t[1].lower() in ast.valid_bit_expr_operators

def parse_collation():
    if t is None or t[0] != Token.Other:
        return

    ttype, value = t
    next_token()
    return ast.Expression(value, 'collation')

def parse_simple_expr_term():
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

    if is_operator():
        if value in ast.simple_expr_unary_operators:
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
    expr = parse_simple_expr_term()
    if expr is None or t is None:
        return expr

    ttype, value = t

    if is_operator('||'):
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

    if lexpr is None:
        return

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

    if t is None or lexpr is None:
        return lexpr

    ttype, value = t

    if is_operator():
        lvalue = value.lower()
        if is_operator('not'):
            next_token()
            op = ast.UnaryOp(lvalue)
            op.add_child(parse_predicate(lexpr))
            return op

        if is_operator('sounds'):
            next_token()
            op = ast.Op(lvalue)
            op.add_child(lexpr)

            if is_operator('like'):
                next_token()
                like_op = ast.Op(t[1].lower())
                like_op.add_child(parse_bit_expr())
                op.add_child(like_op)

            return op

        if is_operator('regexp'):
            next_token()
            op = ast.Op(lvalue)
            op.add_child(lexpr)
            op.add_child(parse_bit_expr())
            return op

        if is_operator('like'):
            next_token()
            op = ast.Op(lvalue)
            op.add_child(lexpr)
            op.add_child(parse_simple_expr())

            if t and t[0] in Token.Keyword and t[1].lower() == 'escape':
                escape_op_value = t[1].lower()
                next_token()
                escape_op = ast.Op(escape_op_value)
                escape_op.add_child(parse_simple_expr())
                op.add_child(escape_op)

            return op

        if is_operator('between'):
            next_token()
            op = ast.Op(lvalue)
            op.add_child(lexpr)
            op.add_child(parse_bit_expr())

            if is_operator('and'):
                next_token()
                op.add_child(parse_predicate())

            return op

    return lexpr

def parse_boolean_primary(lexpr=None):
    if lexpr is None:
        lexpr = parse_predicate()

    if not token_is_valid_boolean_primary_operator() or lexpr is None:
        return lexpr

    ttype, value = t
    next_token()

    lvalue = value.lower()
    operator = ast.Op(lvalue)
    operator.add_child(lexpr)

    if t is None:
        return operator

    if lvalue == 'is':
        if is_operator('not'):
            not_op = ast.UnaryOp('not')
            next_token()

            if is_literal('null'):
                next_token()
                not_op.add_child(ast.Expression('null', 'literal'))

            operator.add_child(not_op)
        elif is_literal('null'):
            next_token()
            operator.add_child(ast.Expression('null', 'literal'))
    else:
        operator.add_child(parse_predicate())

    if token_is_valid_boolean_primary_operator():
        return parse_boolean_primary(operator)

    return operator

def parse_expr_term(lexpr=None):
    if token_is_valid_expression_operator() and (t[1] == '!' or t[1].lower() == 'not'):
        expr = ast.UnaryOp(t[1].lower())
        next_token()
        expr.add_child(parse_expr())
        return expr

    if lexpr is None:
        lexpr = parse_boolean_primary()
        if lexpr is None:
           return

    if not token_is_valid_expression_operator() or not is_operator('is'):
        return lexpr

    ttype, value = t
    next_token()

    lvalue = value.lower()
    operator = ast.Op(lvalue)
    operator.add_child(lexpr)

    if is_operator('not'):
        not_op = ast.UnaryOp('not')
        next_token()

        if t and t[1].lower() in ['true', 'false', 'unknown']:
            not_op.add_child(ast.Expression(t[1].lower(), 'literal'))
            next_token()

        operator.add_child(not_op)
    elif t and t[1].lower() in ['true', 'false', 'unknown']:
        operator.add_child(ast.Expression(t[1].lower(), 'literal'))
        next_token()

    return operator

def parse_expr(prev_operator=None):
    lexpr = parse_expr_term()
    if not token_is_valid_expression_operator():
        if prev_operator:
            prev_operator.add_child(lexpr)
            return prev_operator
        return lexpr

    if lexpr is None:
        return

    ttype, value = t
    next_token()

    lvalue = value.lower()
    operator = ast.Op(lvalue)

    if lvalue == 'is':
        return parse_expr_term(lexpr)

    if not prev_operator:
        operator.add_child(lexpr)
        return parse_expr(operator)

    if prev_operator.has_precedance(operator):
        prev_operator.add_child(lexpr)
        operator.add_child(prev_operator)
        return parse_expr(operator)

    operator.add_child(lexpr)
    prev_operator.add_child(parse_expr(operator))
    return prev_operator

def parse_select_stmt():
    next_token()

def parse_statement():
    ttype, value = t

    # if ttype == Token.Reserved:
        # if value.lower() == 'select':
            # return parse_select_stmt()

    return parse_expr()

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


