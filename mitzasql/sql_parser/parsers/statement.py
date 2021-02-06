# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

from .. import parser_factory
from .parser import Parser

class StatementParser(Parser):
    def __init__(self, state):
        super().__init__(state)

    def parse_stmt(self):
        parser = None
        if self.state.is_reserved('select') or self.state.is_open_paren():
            parser = parser_factory.create(parser_factory.SELECT_STMT, self.state)
        elif self.state.is_reserved('insert'):
            parser = parser_factory.create(parser_factory.INSERT_STMT, self.state)
        elif self.state.is_reserved('replace'):
            parser = parser_factory.create(parser_factory.REPLACE_STMT, self.state)
        elif self.state.is_reserved('update'):
            parser = parser_factory.create(parser_factory.UPDATE_STMT, self.state)
        elif self.state.is_reserved('delete'):
            parser = parser_factory.create(parser_factory.DELETE_STMT, self.state)
        elif self.state.is_keyword('do'):
            parser = parser_factory.create(parser_factory.DO_STMT, self.state)
        elif self.state.is_reserved('call'):
            parser = parser_factory.create(parser_factory.CALL_STMT, self.state)
        elif self.state.is_reserved('set'):
            parser = parser_factory.create(parser_factory.SET_STMT, self.state)

        if parser:
            stmt = parser.run()
            self.last_node = parser.last_node
            if stmt is None:
                return self.run()
            return stmt

        expr_parser = parser_factory.create(parser_factory.EXPR, self.state)
        expr = expr_parser.run()
        self.last_node = expr_parser.last_node
        return expr


    def run(self):
        return self.parse_stmt()

