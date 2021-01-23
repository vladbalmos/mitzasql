import mitzasql.sql_parser.ast as ast
import mitzasql.sql_parser.parser_factory as parser_factory
from mitzasql.sql_parser.parsers.parser import Parser
from mitzasql.sql_parser.parsers.mixins import *
import pudb

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
            while self.state and self.is_table_reference():
                table_references.add_child(self.parse_table_reference())
                if self.state.is_comma():
                    self.state.next()
            stmt.add_child(table_references)

        if self.state.is_reserved('from'):
            from_clause = self.accept(ast.Expression, type='from')
            while self.state and self.is_table_reference():
                from_clause.add_child(self.parse_table_reference())
                if self.state.is_comma():
                    self.state.next()

            stmt.add_child(from_clause)

        if self.state.is_reserved('using'):
            using_clause = self.accept(ast.Expression, type='using')
            while self.state and self.is_table_reference():
                using_clause.add_child(self.parse_table_reference())
                if self.state.is_comma():
                    self.state.next()

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
