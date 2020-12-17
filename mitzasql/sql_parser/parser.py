import os
from collections import deque
import mitzasql.sql_parser.tokens as Token
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

def parse(raw_sql):
    # pudb.set_trace();
    stack = []

    tokens = Lexer(raw_sql).tokenize()
    for ttype, value in tokens:
        if ttype == Token.Whitespace:
            continue
        if ttype == Token.Comment:
            continue

        n = Node(ttype, value)

        try:
            prev_node = stack.pop()
        except IndexError:
            stack.append(n)
            continue

        if n.type in Token.Number:
            prev_node.add_child(n)
            stack.append(prev_node)
            continue

        if n.type in Token.Operator:
            if prev_node.type in Token.Operator:
                if operator_has_priority(n.value, prev_node.value):
                    stack.append(prev_node)
                    n.add_child(prev_node.children[-1])
                    prev_node.children[-1] = n
                    stack.append(n)
                    continue

            while len(stack):
                prev_node = stack.pop()

            n.add_child(prev_node)
            stack.append(n)
            continue


        # if ttype in Token.Operator:
            # if prev_node.type in Token.Operator
               # and operator_has_priority(value, prev_node.value):
                   # n.add_child(prev_node.children[-1])
                   # prev_node.children[-1] = n
                   # stack.push(n)
                   # continue

    dfs(stack[0])
