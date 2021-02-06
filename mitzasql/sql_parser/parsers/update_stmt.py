# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

from .. import ast
from .. import parser_factory
from .parser import Parser
from .mixins import *

MODIFIER_KEYWORDS = ('low_priority', 'ignore')

class UpdateStmtParser(Parser, DMSParserMixin, ExprParserMixin):
    def __init__(self, state):
        super().__init__(state)
        self.expr_parser = parser_factory.create(parser_factory.EXPR, state)

    def is_modifier(self):
        if not self.state:
            return False

        if not self.state.is_reserved():
            return False

        return self.state.lcase_value in MODIFIER_KEYWORDS

    def parse_update_stmt(self):
        if not self.state.is_reserved('update'):
            return

        stmt = self.accept(ast.Statement, self.state.value, 'update')

        if self.is_modifier():
            modifier = self.accept(ast.Expression, type='modifier', advance=False)

            while self.state and self.is_modifier():
                modifier.add_child(self.accept(ast.Expression, self.state.value))

            stmt.add_child(modifier)


        table_references = self.accept(ast.Expression, type='table_references', advance=False)
        while self.state and self.is_table_reference():
            table_ref = self.parse_table_reference()
            if table_ref:
                table_references.add_child(table_ref)

            if self.state.is_comma():
                self.state.next()

        stmt.add_child(table_references)

        if self.state.is_reserved('set'):
            set = self.accept(ast.Expression, self.state.value, type='assignment_list')

            while self.state and not self.state.is_semicolon():
                if self.state.is_reserved('where') \
                        or self.state.is_reserved('order') \
                        or self.state.is_reserved('by') \
                        or self.state.is_reserved('limit'):
                            break
                expr = self.parse_expr()
                set.add_child(expr)

                if self.state.is_comma():
                    self.state.next()
            stmt.add_child(set)

        if self.state.is_reserved('where'):
            where_clause = self.parse_where()
            stmt.add_child(where_clause)

        if self.state.is_reserved('order'):
            order_clause = self.parse_order_by()
            stmt.add_child(order_clause)

        if self.state.is_reserved('limit'):
            limit_clause = self.parse_limit()
            stmt.add_child(limit_clause)

        return stmt

    def run(self):
        return self.parse_update_stmt()
