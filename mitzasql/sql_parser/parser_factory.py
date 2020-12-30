import mitzasql.sql_parser.parsers as parsers

STMT = parsers.StatementParser
SELECT_STMT = parsers.SelectStmtParser
EXPR = parsers.ExpressionParser

def create(cls, state):
    parser = cls(state)
    return parser

