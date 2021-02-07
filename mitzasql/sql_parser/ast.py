# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

# Namespace for different type of AST nodes

simple_expr_unary_operators = ['+', '-', '~', '!']

operator_precedance = {
    '^': 0,
    '*': -1,
    '/': -1,
    'div': -1,
    '%': -1,
    'mod': -1,
    '-': -2,
    '+': -2,
    '<<': -3,
    '>>': -3,
    '&': -4,
    '|': -5,
    '=': -6,
    '<=>': -6,
    '>=': -6,
    '>': -6,
    '<=': -6,
    '<': -6,
    '<>': -6,
    '!=': -6,
    'is': -6,
    'like': -6,
    'regexp': -6,
    'in': -6,
    'between': -7,
    'and': -8,
    '&&': -8,
    'xor': -9,
    'or': -10,
    '||': -10,
    ':=': -11,
}

comparison_operators = [
    '=',
    '>=',
    '>',
    '<=',
    '<',
    '<>',
    '!=',
]

valid_expression_operators = [
    'or',
    '||',
    'xor',
    'and',
    '&&',
    'not',
    'is'
]

valid_boolean_primary_operators = [
    'is',
    '=',
    ':=',
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

valid_predicate_operators = [
    'in',
    'between',
    'sounds',
    'like',
    'regexp'
]

class NodeMixin:
    def __init__(self, value=None, type=None, pos=None):
        self.value = value
        self.type = type
        self.pos = pos
        self.parent = None
        self.children = []

    def __repr__(self):
        repr_ = str(self.type);
        if self.value is not None:
            repr_ += ':' + str(self.value) + ':' + str(self.pos)

        return repr_

    def add_child(self, child):
        if child is None:
            return
        child.parent = self
        self.children.append(child)

    def get_last_child(self):
        if not self.has_children():
            return self

        child = self.children[-1]
        return child.get_last_child()

    def get_first_child(self, type):
        if not self.has_children():
            return

        for child in self.children:
            if child.type == type:
                return child

    def get_child(self, type):
        if not self.has_children():
            return

        for child in self.children:
            if child.type == type:
                return child
            child_ = child.get_child(type)
            if child_ is None:
                continue
            return child_

    def has_children(self):
        return len(self.children) > 0

class Statement(NodeMixin):
    def __init__(self, value=None, type='statement', pos=None):
        super().__init__(value, type, pos)

class Expression(NodeMixin):
    def __init__(self, value=None, type='expression', pos=None):
        super().__init__(value, type, pos)

class Op(NodeMixin):
    def __init__(self, value, type='operator', pos=None):
        super().__init__(value, type, pos)

    def has_precedance(self, operator):
        own_priority = operator_precedance[self.value.lower()]
        op_priority = operator_precedance[operator.value.lower()]

        return own_priority >= op_priority

class UnaryOp(Op):
    def __init__(self, value, type="unary_operator", pos=None):
        super().__init__(value, type, pos)

    def has_precedance(self, operator):
        return True
