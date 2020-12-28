import mitzasql.sql_parser.parsers as parsers

STMT = parsers.StatementParser
EXPR = parsers.ExpressionParser

def create(cls, state):
    parser = cls(state)
    return parser

