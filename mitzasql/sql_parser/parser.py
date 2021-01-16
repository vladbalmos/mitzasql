# TODO:
    # - fix parsing joins
    # - fix parsing union

from mitzasql.sql_parser.lexer import Lexer
from mitzasql.sql_parser.state import State
from mitzasql.utils import dfs
import mitzasql.sql_parser.parser_factory as parser_factory

last_parsed_node = None

def parse(raw_sql):
    global last_parsed_node
    tokens = Lexer(raw_sql).tokenize()
    state = State(tokens)
    statements = []

    parser = parser_factory.create(parser_factory.STMT, state)

    while state:
        stmt = parser.run()
        last_parsed_node = parser.last_node
        # dfs(stmt)
        statements.append(stmt)

    return statements

def get_last_parsed_node():
    return last_parsed_node

