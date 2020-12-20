import os
import itertools
from collections import deque
import mitzasql.sql_parser.tokens as Token
import mitzasql.sql_parser.ast as ast
from mitzasql.sql_parser.lexer import Lexer
import pudb

operator_precedance = {
    'INTERVAL': 0,
    'COLLATE': -1,
    '!': -2,
    '-': -3,
    '~': -3,
    '^': -4,
    '*': -5,
    '/': -5,
    'DIV': -5,
    '%': -5,
    'MOD': -5,
    '-': -6,
    '+': -6
}

def dfs(root, padding_left=0):
    if padding_left == 0:
        print('\n')

    print(''.rjust(padding_left, ' ') + str(root))

    for child in root.children:
        dfs(child, padding_left + 5)


class Node:
    def __init__(self, ttype, value):
        self.type = ttype
        self.value = value
        self.parent = None
        self.children = []

    def __repr__(self):
        return str(self.type) + ':' + str(self.value)

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

def operator_has_priority(op1, op2):
    op1_priority = operator_precedance[op1]
    op2_priority = operator_precedance[op2]

    return op1_priority > op2_priority

def parse_expression(tokens, current_token=None):
    print('\n')
    expr = None
    stack = []
    postfix = []

    if current_token:
        tokens = itertools.chain([current_token], tokens)

    for ttype, value in tokens:
        if ttype == Token.Whitespace:
            continue
        if ttype == Token.Comment:
            continue
        if ttype == Token.Comma:
            break

        if ttype in Token.Literal:
            postfix.append(value)
            continue

        if ttype in Token.Operator:
            if not len(stack):
                stack.append(value)
                continue

            while len(stack):
                if ast.operator_precedance[stack[-1]] >= operator_precedance[value]:
                    postfix.append(stack.pop())
                    continue
                break
            stack.append(value)


    while len(stack):
        postfix.append(stack.pop())

    print(''.join(postfix))

    expr = ast.Expression(type='expr')

    # if len(stack):
        # expr.add_child(stack[0])

    # while len(stack):
        # dfs(stack.pop())

    return expr

def parse_select_stmt(tokens):
    pass

def parse_statement(tokens):
    stmt = None
    for ttype, value in tokens:
        # pudb.set_trace();
        if ttype == Token.Whitespace:
            continue
        if ttype == Token.Comment:
            continue
        if ttype == Token.Semicolon:
            return stmt

        if ttype == Token.Reserved:
            if value.lower() == 'select':
                stmt = parse_select_stmt(tokens)
                continue

        stmt = parse_expression(tokens, current_token=(ttype, value))
    return stmt

def parse(raw_sql):
    statements = []
    tokens = Lexer(raw_sql).tokenize()

    while True:
        stmt = parse_statement(tokens)
        if not stmt:
            break

        statements.append(stmt)

    dfs(statements[0])

    return statements

# def parse(raw_sql):
    # # pudb.set_trace();
    # nodes = []

    # tokens = Lexer(raw_sql).tokenize()
    # for ttype, value in tokens:
        # if ttype == Token.Whitespace:
            # continue
        # if ttype == Token.Comment:
            # continue

        # expr = parse_expression(ttype, value, tokens)
        # n = Node(ttype, value)

        # try:
            # prev_node = stack.pop()
        # except IndexError:
            # stack.append(n)
            # continue

        # if n.type in Token.Number:
            # prev_node.add_child(n)
            # stack.append(prev_node)
            # continue

        # if n.type in Token.Operator:
            # if prev_node.type in Token.Operator:
                # if operator_has_priority(n.value, prev_node.value):
                    # stack.append(prev_node)
                    # n.add_child(prev_node.children[-1])
                    # prev_node.children[-1] = n
                    # stack.append(n)
                    # continue

            # while len(stack):
                # prev_node = stack.pop()

            # n.add_child(prev_node)
            # stack.append(n)
            # continue

    # dfs(stack[0])
