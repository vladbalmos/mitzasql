from mitzasql.sql_parser.lexer import Lexer
from mitzasql.sql_parser.state import State
from mitzasql.sql_parser.parser_factory import create_parser

def parse(raw_sql):
    tokens = Lexer(raw_sql).tokenize()
    state = State(tokens)
    statements = []

    parse_statement = create_parser('stmt', state)

    while state.is_valid():
        stmt = parse_statement()
        statements.append(stmt)

    return statements

