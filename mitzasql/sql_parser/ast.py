operator_precedance = {
    'interval': 0,
    'binary': -1,
    'collate': -1,
    '!': -2,
    # unary minus and unary bit inversion is -3
    '^': -4,
    '*': -5,
    '/': -5,
    'div': -5,
    '%': -5,
    'mod': -5,
    '-': -6,
    '+': -6

}
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
        child.parent = self
        self.children.append(child)

class Statement(NodeMixin):
    def __init__(self):
        super().__init__()

class Expression(NodeMixin):
    def __init__(self, value=None, type=None):
        super().__init__(value, type)

class Operator(NodeMixin):
    def __init__(self, value):
        super().__init__(value, 'operator')

    def has_precedance(self, operator):
        own_priority = operator_precedance[self.value.lower()]
        op_priority = operator_precedance[operator.value.lower()]

        return own_priority > op_priority
