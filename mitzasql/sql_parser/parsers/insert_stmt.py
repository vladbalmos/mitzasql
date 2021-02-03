from .. import ast
from .. import parser_factory
from .parser import Parser
from .mixins import *

MODIFIER_KEYWORDS = ('low_priority', 'high_priority', 'ignore', 'delayed')

class InsertStmtParser(Parser, DMSParserMixin, ExprParserMixin):
    def __init__(self, state):
        super().__init__(state)
        self.expr_parser = parser_factory.create(parser_factory.EXPR, state)
        self.select_parser = parser_factory.create(parser_factory.SELECT_STMT, state)

    def is_modifier(self):
        if not self.state:
            return False

        if not self.state.is_reserved():
            return False

        return self.state.lcase_value in MODIFIER_KEYWORDS

    def parse_values(self):
        values = self.accept(ast.Expression, self.state.value, type='values')
        while self.state and self.state.is_open_paren():
            values.add_child(self.parse_expr())

            if self.state.is_comma():
                self.state.next()

        return values

    def parse_insert_stmt(self):
        if not self.state.is_reserved('insert'):
            return

        stmt = self.accept(ast.Statement, self.state.value, 'insert')

        if self.is_modifier():
            modifier = self.accept(ast.Expression, type='modifier', advance=False)

            while self.state and self.is_modifier():
                modifier.add_child(self.accept(ast.Expression, self.state.value))

            stmt.add_child(modifier)

        if self.state.is_reserved('into'):
            into = self.accept(ast.Expression, self.state.value, type='into')
            if self.is_table_reference():
                into.add_child(self.parse_table_reference())
                stmt.add_child(into)

        if self.state.is_reserved('set'):
            set = self.accept(ast.Expression, self.state.value, type='assignment_list')

            while self.state and not self.state.is_semicolon():
                if self.state.is_reserved('on'):
                    break

                expr = self.parse_expr()
                set.add_child(expr)

                if self.state.is_comma():
                    self.state.next()

            stmt.add_child(set)
        elif self.state.is_open_paren():
            columns = self.accept(ast.Expression, type='columns', advance=False)
            columns.add_child(self.parse_expr())
            stmt.add_child(columns)

        if self.state.is_reserved('select'):
            select = self.select_parser.run()
            self.last_node = self.select_parser.last_node
            stmt.add_child(select)
        elif self.state.lcase_value == 'value' or self.state.lcase_value == 'values':
            stmt.add_child(self.parse_values())

        if self.state.is_reserved('on'):
            on = self.accept(ast.Expression, self.state.value, type='on')
            if self.state.is_keyword('duplicate'):
                duplicate = self.accept(ast.Expression, self.state.value, type='duplicate')
                on.add_child(duplicate)

                if self.state.is_reserved('key'):
                    key = self.accept(ast.Expression, self.state.value, type='key')
                    duplicate.add_child(key)

                    if self.state.is_reserved('update'):
                        update = self.accept(ast.Expression, self.state.value, type='update')
                        key.add_child(update)

                        while self.state and not self.state.is_semicolon():
                            expr = self.parse_expr()
                            update.add_child(expr)
                            if self.state.is_comma():
                                self.state.next()

            stmt.add_child(on)

        return stmt

    def run(self):
        return self.parse_insert_stmt()