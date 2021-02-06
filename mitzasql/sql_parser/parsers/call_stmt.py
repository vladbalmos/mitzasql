# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

from .. import ast
from .. import parser_factory
from .parser import Parser
from .mixins import *

class CallStmtParser(Parser, ExprParserMixin):
    def __init__(self, state):
        super().__init__(state)
        self.expr_parser = parser_factory.create(parser_factory.EXPR, state)

    def parse_call_stmt(self):
        if not self.state.is_reserved('call'):
            return

        stmt = self.accept(ast.Statement, self.state.value, 'call')

        if not self.state or self.state.is_semicolon():
            return stmt

        proc = self.accept(ast.Expression, type='proc', advance=False)
        expr = self.parse_expr()
        if expr:
            proc.add_child(expr)
            stmt.add_child(proc)
        return stmt

    def run(self):
        return self.parse_call_stmt()
