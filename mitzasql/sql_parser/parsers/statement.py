import mitzasql.sql_parser.parser_factory as parser_factory
from mitzasql.sql_parser.parsers.parser import Parser

class StatementParser(Parser):
    def __init__(self, state):
        super().__init__(state)

    def parse_stmt(self):
        if self.state.is_reserved('select') or self.state.is_open_paren():
            select_parser = parser_factory.create(parser_factory.SELECT_STMT, self.state)
            stmt = select_parser.run()
            self.last_node = select_parser.last_node
            if stmt is None:
                return self.run()
            return stmt

        if self.state.is_reserved('update'):
            update_parser = parser_factory.create(parser_factory.UPDATE_STMT, self.state)
            stmt = update_parser.run()
            self.last_node = update_parser.last_node
            if stmt is None:
                return self.run()
            return stmt


        expr_parser = parser_factory.create(parser_factory.EXPR, self.state)
        expr = expr_parser.run()
        self.last_node = expr_parser.last_node
        return expr


    def run(self):
        return self.parse_stmt()

