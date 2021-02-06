# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

from .. import ast
from .. import parser_factory
from .parser import Parser
from .mixins import *

class DoStmtParser(Parser, ExprParserMixin):
    def __init__(self, state):
        super().__init__(state)
        self.expr_parser = parser_factory.create(parser_factory.EXPR, state)

    def parse_do_stmt(self):
        if not self.state.is_keyword('do'):
            return

        stmt = self.accept(ast.Statement, self.state.value, 'do')

        while self.state and not self.state.is_semicolon():
            expr = self.parse_expr()
            if expr:
                stmt.add_child(expr)

            if self.state.is_comma():
                self.state.next()

        if self.state.is_semicolon():
            self.state.next()

        return stmt

    def run(self):
        return self.parse_do_stmt()
