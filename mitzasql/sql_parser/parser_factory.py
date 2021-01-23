import mitzasql.sql_parser.parsers as parsers

STMT = parsers.StatementParser
SELECT_STMT = parsers.SelectStmtParser
UPDATE_STMT = parsers.UpdateStmtParser
EXPR = parsers.ExpressionParser

def create(cls, state):
    parser = cls(state)
    return parser

