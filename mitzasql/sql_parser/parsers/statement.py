import mitzasql.sql_parser.parser_factory as parser_factory

class StatementParser:
    def __init__(self, state):
        self.state = state
        self.last_node = None

    def parse_stmt(self):
        if self.state.is_reserved('select'):
            select_parser = parser_factory.create(parser_factory.SELECT_STMT, self.state)
            stmt = select_parser.run()
            self.last_node = select_parser.last_node
            if stmt is None:
                return self.parse_stmt()
            return stmt


        expr_parser = parser_factory.create(parser_factory.EXPR, self.state)
        expr = expr_parser.run()
        self.last_node = expr_parser.last_node
        return expr


    def run(self):
        return self.parse_stmt()

