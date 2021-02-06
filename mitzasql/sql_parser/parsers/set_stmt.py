# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

from .. import ast
from .. import parser_factory
from .parser import Parser
from .mixins import *

class SetStmtParser(Parser, ExprParserMixin):
    def __init__(self, state):
        super().__init__(state)
        self.expr_parser = parser_factory.create(parser_factory.EXPR, state)

    def parse_variable(self):
        prepend_to_var = ''
        if self.state.lcase_value in ('global', 'session', 'local'):
            prepend_to_var = '@@' + self.state.value + '.'
            self.state.next()

        var = self.accept(ast.Expression, type='variable', advance=False)
        expr = self.parse_expr()
        if expr is None:
            return

        if expr.type == 'operator' and expr.has_children():
            expr.children[0].value = prepend_to_var + expr.children[0].value

        var.add_child(expr)

        return var

    def parse_names(self):
        names = self.accept(ast.Expression, self.state.value, type='names')
        if self.state.is_literal() or self.state.is_other():
            names.add_child(self.parse_expr())

        if self.state.is_reserved('collate'):
            collate = self.accept(ast.Expression, self.state.value, type='collate')

            if self.state.is_literal() or self.state.is_other():
                collate.add_child(self.parse_expr())
            names.add_child(collate)
        elif self.state.is_reserved('default'):
            names.add_child(self.accept(ast.Expression, self.state.value, type='default'))

        return names

    def parse_charset(self):
        charset = None
        charset_ = None
        if self.state.is_reserved('character'):
            charset = self.accept(ast.Expression, self.state.value, type='character')

            if not self.state.is_reserved('set'):
                return charset

            charset_ = self.accept(ast.Expression, self.state.value, type='set')
            charset.add_child(charset_)
        else:
            charset = self.accept(ast.Expression, self.state.value, type='charset')
            charset_ = charset

        charset_.add_child(self.parse_expr())
        return charset

    def parse_set_stmt(self):
        if not self.state.is_reserved('set'):
            return

        stmt = self.accept(ast.Statement, self.state.value, 'set')

        while self.state and not self.state.is_semicolon():
            if self.state.is_keyword('names'):
                stmt.add_child(self.parse_names())
                continue

            if self.state.is_reserved('character') or self.state.lcase_value == 'charset':
                stmt.add_child(self.parse_charset())
                continue

            stmt.add_child(self.parse_variable())

            if self.state.is_comma():
                self.state.next()

        if self.state.is_semicolon():
            self.state.next()

        return stmt

    def run(self):
        return self.parse_set_stmt()
