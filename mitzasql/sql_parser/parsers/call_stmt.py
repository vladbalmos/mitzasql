import mitzasql.sql_parser.ast as ast
import mitzasql.sql_parser.parser_factory as parser_factory
from mitzasql.sql_parser.parsers.parser import Parser
from mitzasql.sql_parser.parsers.mixins import *
import pudb

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

        if not (self.state.lcase_value.isalnum() and not self.state.lcase_value.isnumeric()):
            return stmt

        proc = self.accept(ast.Expression, type='proc', advance=False)
        expr = self.parse_expr()
        if expr:
            proc.add_child(expr)
            stmt.add_child(proc)
        return stmt

    def run(self):
        return self.parse_call_stmt()
