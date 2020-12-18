class Statement:
    def __init__(self):
        self.children = []

class Expression():
    def __init__(self, value=None, type=None):
        self.value = value
        self.type = type
        self.parent = None
        self.children = []

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

class Node:
    def __init__(self, value, node_type):
        self.value = value
        self.type = node_type
        self.children = []

    def __repr__(self):
        return str(self.type) + ':' + str(self.value)

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

class Operator(Node):
    def __init__(self, value):
        super.__init__(self, value, 'operator')

    def is_unary(self):
        return value == '!' or value == '-' or value == '~'
