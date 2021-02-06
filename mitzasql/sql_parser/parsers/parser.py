# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

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

    def run(self):
        raise NotImplementedError('Parser method must be implemented in subclass')

