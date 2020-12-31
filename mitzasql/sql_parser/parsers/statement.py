import mitzasql.sql_parser.parser_factory as parser_factory

class StatementParser:
    def __init__(self, state):
        self.state = state

    def parse_stmt(self):
        if self.state.is_reserved('select'):
            select_parser = parser_factory.create(parser_factory.SELECT_STMT, self.state)
            stmt = select_parser.run()
            if stmt is None:
                return self.parse_stmt()
            return stmt


        expr_parser = parser_factory.create(parser_factory.EXPR, self.state)
        return expr_parser.run()


    def run(self):
        return self.parse_stmt()

