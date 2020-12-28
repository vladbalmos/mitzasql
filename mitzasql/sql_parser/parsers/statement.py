import mitzasql.sql_parser.parser_factory as parser_factory

class StatementParser:
    def __init__(self, state):
        self.state = state
        self.expr_parser = parser_factory.create(parser_factory.EXPR, state)

    def parse_expr(self):
        return self.expr_parser.run()


    def run(self):
        return self.parse_expr()

