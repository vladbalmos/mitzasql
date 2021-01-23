import mitzasql.sql_parser.ast as ast
import mitzasql.sql_parser.parser_factory as parser_factory
from mitzasql.sql_parser.parsers.parser import Parser
from mitzasql.sql_parser.parsers.mixins import *
import pudb

UPDATE_MODIFIER_KW = ('low_priority', 'ignore')

class DeleteStmtParser(Parser, DMSParserMixin, ExprParserMixin):
    def __init__(self, state):
        super().__init__(state)
        self.expr_parser = parser_factory.create(parser_factory.EXPR, state)

    def is_update_modifier(self):
        if not self.state:
            return False

        if not self.state.is_reserved():
            return False

        return self.state.lcase_value in UPDATE_MODIFIER_KW

    def parse_update_stmt(self):
        if not self.state.is_reserved('update'):
            return

        stmt = self.accept(ast.Statement, self.state.value, 'update')

        if self.is_update_modifier():
            modifier = self.accept(ast.Expression, type='modifier', advance=False)

            while self.state and self.is_update_modifier():
                modifier.add_child(self.accept(ast.Expression, self.state.value))

            stmt.add_child(modifier)


        table_references = self.accept(ast.Expression, type='table_references', advance=False)
        while self.state and self.is_table_reference():
            table_references.add_child(self.parse_table_reference())
            if self.state.is_comma():
                self.state.next()

        stmt.add_child(table_references)

        if self.state.is_reserved('set'):
            set = self.accept(ast.Expression, self.state.value, type='assignment_list')

            while self.state:
                if self.state.is_reserved('where') \
                        or self.state.is_reserved('order') \
                        or self.state.is_reserved('by') \
                        or self.state.is_reserved('limit'):
                            break
                expr = self.parse_expr()
                if expr:
                    set.add_child(expr)
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
