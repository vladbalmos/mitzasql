import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer

def parse(raw_sql):
    tokens = Lexer(raw_sql).tokenize()
    stack = []
    expr = ''
    for ttype, value in tokens:
        if ttype == Token.Whitespace:
            continue

        if ttype in Token.Number:
            expr += value
            continue

        if ttype in Token.Operator:
            if not len(stack):
                stack.append(value)
                continue

            if value == '-':
                expr += stack.pop()
                stack.append(value)
                continue

            if value == '*':
                stack.append(value)
                continue

    while len(stack):
        expr += stack.pop()

    print(expr)


