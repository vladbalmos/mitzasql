import mitzasql.sql_parser.parsers as parsers

STMT = parsers.StatementParser
SELECT_STMT = parsers.SelectStmtParser
UPDATE_STMT = parsers.UpdateStmtParser
INSERT_STMT = parsers.InsertStmtParser
DELETE_STMT = parsers.DeleteStmtParser
DO_STMT = parsers.DoStmtParser
CALL_STMT = parsers.CallStmtParser
SET_STMT = parsers.SetStmtParser
EXPR = parsers.ExpressionParser

def create(cls, state):
    parser = cls(state)
    return parser

