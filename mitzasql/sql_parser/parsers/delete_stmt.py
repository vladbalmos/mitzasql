# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

from .. import ast
from .. import parser_factory
from .parser import Parser
from .mixins import *

MODIFIER_KEYWORDS = ('low_priority', 'quick', 'ignore')

class DeleteStmtParser(Parser, DMSParserMixin, ExprParserMixin):
    def __init__(self, state):
        super().__init__(state)
        self.expr_parser = parser_factory.create(parser_factory.EXPR, state)

    def is_modifier(self):
        if not self.state:
            return False

        if not self.state.is_reserved():
            return False

        return self.state.lcase_value in MODIFIER_KEYWORDS

    def parse_table_refs(self, parent_stmt):
        while self.state and self.is_table_reference():
            table_ref = self.parse_table_reference()
            if table_ref:
                parent_stmt.add_child(table_ref)

            if self.state.is_comma():
                self.state.next()

    def parse_delete_stmt(self):
        if not self.state.is_reserved('delete'):
            return

        stmt = self.accept(ast.Statement, self.state.value, 'delete')

        if self.is_modifier():
            modifier = self.accept(ast.Expression, type='modifier', advance=False)

            while self.state and self.is_modifier():
                modifier.add_child(self.accept(ast.Expression, self.state.value))

            stmt.add_child(modifier)

        if self.state.lcase_value not in ('from', 'where', 'order', 'limit') and self.is_table_reference():
            table_references = self.accept(ast.Expression, type='table_references', advance=False)
            self.parse_table_refs(table_references)
            stmt.add_child(table_references)

        if self.state.is_reserved('from'):
            from_clause = self.accept(ast.Expression, type='from')
            self.parse_table_refs(from_clause)
            stmt.add_child(from_clause)

        if self.state.is_reserved('using'):
            using_clause = self.accept(ast.Expression, type='using')
            self.parse_table_refs(using_clause)
            stmt.add_child(using_clause)

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
        return self.parse_delete_stmt()
