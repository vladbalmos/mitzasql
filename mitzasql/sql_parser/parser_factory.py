import mitzasql.sql_parser.parsers as parsers

STMT = parsers.StatementParser
SELECT_STMT = parsers.SelectStmtParser
UPDATE_STMT = parsers.UpdateStmtParser
DELETE_STMT = parsers.DeleteStmtParser
EXPR = parsers.ExpressionParser

def create(cls, state):
    parser = cls(state)
    return parser

