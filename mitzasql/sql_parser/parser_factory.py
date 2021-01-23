import mitzasql.sql_parser.parsers as parsers

STMT = parsers.StatementParser
SELECT_STMT = parsers.SelectStmtParser
UPDATE_STMT = parsers.UpdateStmtParser
DELETE_STMT = parsers.DeleteStmtParser
DO_STMT = parsers.DoStmtParser
CALL_STMT = parsers.CallStmtParser
EXPR = parsers.ExpressionParser

def create(cls, state):
    parser = cls(state)
    return parser

