import mitzasql.sql_parser.parser_factory as parser_factory
from mitzasql.sql_parser.parsers.parser import Parser

class StatementParser(Parser):
    def __init__(self, state):
        super().__init__(state)

    def parse_stmt(self):
        parser = None
        if self.state.is_reserved('select') or self.state.is_open_paren():
            parser = parser_factory.create(parser_factory.SELECT_STMT, self.state)
        elif self.state.is_reserved('update'):
            parser = parser_factory.create(parser_factory.UPDATE_STMT, self.state)
        elif self.state.is_reserved('delete'):
            parser = parser_factory.create(parser_factory.DELETE_STMT, self.state)

        if parser:
            stmt = parser.run()
            self.last_node = parser.last_node
            if stmt is None:
                return self.run()
            return stmt

        expr_parser = parser_factory.create(parser_factory.EXPR, self.state)
        expr = expr_parser.run()
        self.last_node = expr_parser.last_node
        return expr


    def run(self):
        return self.parse_stmt()

