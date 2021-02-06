# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

from .lexer import Lexer
from .state import State
from . import parser_factory
from mitzasql.utils import dfs

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
        statements.append(stmt)

        if state and state.is_semicolon():
            state.next()

    return statements

def get_last_parsed_node():
    return last_parsed_node

