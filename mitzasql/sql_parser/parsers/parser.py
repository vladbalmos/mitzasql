class Parser:
    def __init__(self, state):
        self.state = state
        self.last_node = None

    def accept(self, cls, *args, **kwargs):
        advance_state = True

        if 'advance' in kwargs:
            advance_state = kwargs['advance']
            kwargs.pop('advance')

        kwargs['pos'] = self.state.pos
        node = cls(*args, **kwargs)
        self.last_node = node

        if advance_state:
            self.state.next()
        return node


