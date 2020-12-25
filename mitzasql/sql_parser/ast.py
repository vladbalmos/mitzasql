unary_operators = ['+', '-', '~', '!']

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
    'and': -9,
    '&&': -10,
    'xor': -11,
    'or': -12,
    '||': -12,
    ':=': -13,
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
    '!',
    'is'
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

class NodeMixin:
    def __init__(self, value=None, type=None):
        self.value = value
        self.type = type
        self.parent = None
        self.children = []

    def __repr__(self):
        repr_ = str(self.type);
        if self.value is not None:
            repr_ += ':' + str(self.value)

        return repr_

    def add_child(self, child):
        if child is None:
            return
        child.parent = self
        self.children.append(child)

    def has_children(self):
        return len(self.children) > 0

class Statement(NodeMixin):
    def __init__(self):
        super().__init__()

class Expression(NodeMixin):
    def __init__(self, value=None, type='expression'):
        super().__init__(value, type)

class Op(NodeMixin):
    def __init__(self, value, type='operator'):
        super().__init__(value, type)

    def has_precedance(self, operator):
        own_priority = operator_precedance[self.value.lower()]
        op_priority = operator_precedance[operator.value.lower()]

        return own_priority >= op_priority

class UnaryOp(Op):
    def __init__(self, value, type="unary_operator"):
        super().__init__(value, type)

    def has_precedance(self, operator):
        return True
