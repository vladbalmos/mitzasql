# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

from .. import ast
from .. import parser_factory
from .parser import Parser
from .mixins import *

MODIFIER_KEYWORDS = ('all', 'distinct', 'distinctrow',
        'high_priority', 'straight_join', 'sql_small_result',
        'sql_big_result', 'sql_buffer_result', 'sql_cache',
        'sql_no_cache', 'sql_calc_found_rows')

class SelectStmtParser(Parser, DMSParserMixin, ExprParserMixin):
    def __init__(self, state):
        super().__init__(state)
        self.expr_parser = parser_factory.create(parser_factory.EXPR, state)

    def is_modifier(self):
        if not self.state:
            return False

        if not self.state.is_keyword():
            return False

        return self.state.lcase_value in MODIFIER_KEYWORDS

    def is_select_expr(self):
        if not self.state or self.state.is_semicolon():
            return False

        if self.state.is_literal() or self.state.is_name() or self.state.is_other():
            return True

        return self.state.lcase_value not in COL_TERMINATOR_KEYWORDS

    def parse_col(self):
        col  = self.accept(ast.Expression, type='column', advance=False)
        expr = self.parse_expr()

        col.add_child(expr)

        if self.state.is_column_alias():
            alias = self.parse_alias()
            col.add_child(alias)
            return col

        if self.state.is_comma():
            self.state.next()

        return col

    def parse_outfile_charset(self):
        if not self.state.is_reserved('character'):
            return

        charset = self.accept(ast.Expression, self.state.value, type='character')

        if not self.state.is_reserved('set'):
            return charset

        set = self.accept(ast.Expression, self.state.value, type='set')
        charset.add_child(set)

        if not self.state.is_literal() and not self.state.is_other():
            return charset

        set.add_child(self.accept(ast.Expression, self.state.value, 'charset'))
        return charset

    def parse_outfile_export_expr(self):
        if not self.state.is_keyword() or self.state.lcase_value not in ('fields', 'columns', 'lines'):
            return

        def parse_by():
            if not self.state.is_reserved('by'):
                return

            by = self.accept(ast.Expression, self.state.value, type='by')

            if not self.state.is_literal:
                return by

            by.add_child(self.accept(ast.Expression, self.state.value, 'literal'))
            return by

        expr = None
        if self.state.is_reserved('lines'):
            expr = self.accept(ast.Op, self.state.value)
            if self.state.is_reserved('starting'):
                starting = self.accept(ast.UnaryOp, self.state.value)
                if self.state.is_reserved('by'):
                    starting.add_child(parse_by())
                expr.add_child(starting)

            if self.state.is_reserved('terminated'):
                terminated = self.accept(ast.UnaryOp, self.state.value)
                if self.state.is_reserved('by'):
                    terminated.add_child(parse_by())
                expr.add_child(terminated)

            return expr

        if self.state.is_keyword('fields') or self.state.is_keyword('columns'):
            expr = self.accept(ast.Op, self.state.value)

            if self.state.is_reserved('terminated'):
                terminated = self.accept(ast.UnaryOp, self.state.value)
                if self.state.is_reserved('by'):
                    terminated.add_child(parse_by())
                expr.add_child(terminated)

            optionally = None

            if self.state.is_reserved('optionally'):
                optionally = self.accept(ast.UnaryOp, self.state.value)
                expr.add_child(optionally)

            if self.state.is_reserved('enclosed'):
                enclosed = self.accept(ast.UnaryOp, self.state.value)

                if self.state.is_reserved('by'):
                    enclosed.add_child(parse_by())

                if optionally is not None:
                    optionally.add_child(enclosed)
                else:
                    expr.add_child(enclosed)

            if self.state.is_reserved('escaped'):
                escaped = self.accept(ast.UnaryOp, self.state.value)

                if self.state.is_reserved('by'):
                    escaped.add_child(parse_by())

                expr.add_child(escaped)

        return expr

    def parse_into(self):
        if not self.state.is_reserved('into'):
            return

        into = self.accept(ast.UnaryOp, self.state.value)

        if self.state.is_variable():
            while self.state and self.state.is_variable():
                var = self.accept(ast.Expression, self.state.value, 'variable')
                into.add_child(var)
                if self.state.is_comma():
                    self.next_state()
            return into

        if self.state.is_keyword('dumpfile'):
            dumpfile = self.accept(ast.Op, self.state.value)
            if self.state.is_literal():
                dumpfile.add_child(self.accept(ast.Expression, self.state.value, 'literal'))

            into.add_child(dumpfile)
            return into

        if self.state.is_reserved('outfile'):
            outfile = self.accept(ast.Op, self.state.value)
            into.add_child(outfile)

            if not self.state.is_literal():
                return into

            outfile.add_child(self.accept(ast.Expression, self.state.value, 'literal'))

            if self.state.is_reserved('character'):
                outfile.add_child(self.parse_outfile_charset())

            if self.state.is_keyword() and self.state.lcase_value in ('fields', 'columns', 'lines'):
                outfile.add_child(self.parse_outfile_export_expr())

        return into

    def parse_from(self):
        if not self.state.is_reserved('from'):
            return

        from_clause = self.accept(ast.Expression, type='from')

        while self.state and self.is_table_reference():
            from_clause.add_child(self.parse_table_reference())
            if self.state.is_comma():
                self.state.next()

        return from_clause

    def parse_group_by(self):
        if not self.state.is_reserved('group'):
            return

        group = self.accept(ast.Op, self.state.value)

        if not self.state.is_reserved('by'):
            return group

        by = self.accept(ast.Op, self.state.value)
        group.add_child(by)

        while self.state:
            expr = self.parse_order_expr()
            if expr is None:
                break
            by.add_child(expr)

            if self.state.is_comma():
                self.state.next()
                continue
            break

        if self.state.is_reserved('with'):
            with_ = self.accept(ast.UnaryOp, self.state.value)
            if self.state.is_keyword('rollup'):
                rollup = self.accept(ast.UnaryOp, self.state.value)
                with_.add_child(rollup)

            group.add_child(with_)

        return group

    def parse_having(self):
        if not self.state.is_reserved('having'):
            return

        where_clause = self.accept(ast.Expression, type='having')
        where_clause.add_child(self.parse_expr())
        return where_clause

    def parse_procedure(self):
        if not self.state.is_reserved('procedure'):
            return

        procedure = self.accept(ast.UnaryOp, self.state.value)
        if self.state.is_function_call():
            procedure.add_child(self.parse_expr())

        return procedure

    def parse_for_clause(self):
        if not self.state.is_reserved('for'):
            return

        for_ = self.accept(ast.UnaryOp, self.state.value)

        if self.state.is_reserved('update'):
            for_.add_child(self.accept(ast.UnaryOp, self.state.value))

        return for_

    def parse_lock_clause(self):
        if not self.state.is_reserved('lock'):
            return

        lock = self.accept(ast.UnaryOp, self.state.value)

        if not self.state.is_reserved('in'):
            return lock
        lock.add_child(self.accept(ast.UnaryOp, self.state.value))

        if not self.state.is_keyword('share'):
            return lock
        lock.add_child(self.accept(ast.UnaryOp, self.state.value))

        if not self.state.is_keyword('mode'):
            return lock
        lock.add_child(self.accept(ast.UnaryOp, self.state.value))

        return lock

    def parse_select_body(self):
        stmt = self.accept(ast.Statement, self.state.value, 'select')

        if self.is_modifier():
            modifier = self.accept(ast.Expression, type='modifier', advance=False)

            while self.state and self.is_modifier():
                modifier.add_child(self.accept(ast.Expression, self.state.value))

            stmt.add_child(modifier)

        columns = self.accept(ast.Expression, type='columns', advance=False)
        stmt.add_child(columns)
        while self.state and self.is_select_expr():
            col = self.parse_col()
            columns.add_child(col)

        if self.state.is_reserved('into'):
            into_clause = self.parse_into()
            stmt.add_child(into_clause)

        if self.state.is_reserved('from'):
            from_clause = self.parse_from()
            stmt.add_child(from_clause)

        if self.state.is_reserved('where'):
            where_clause = self.parse_where()
            stmt.add_child(where_clause)

        if self.state.is_reserved('group'):
            group_clause = self.parse_group_by()
            stmt.add_child(group_clause)

        if self.state.is_reserved('having'):
            having_clause = self.parse_having()
            stmt.add_child(having_clause)

        if self.state.is_reserved('order'):
            order_clause = self.parse_order_by()
            stmt.add_child(order_clause)

        if self.state.is_reserved('limit'):
            limit_clause = self.parse_limit()
            stmt.add_child(limit_clause)

        if self.state.is_reserved('procedure'):
            procedure_clause = self.parse_procedure()
            stmt.add_child(procedure_clause)

        if self.state.is_reserved('into'):
            into_clause = self.parse_into()
            stmt.add_child(into_clause)

        if self.state.is_reserved('for'):
            for_clause = self.parse_for_clause()
            stmt.add_child(for_clause)

        if self.state.is_reserved('lock'):
            lock_clause = self.parse_lock_clause()
            stmt.add_child(lock_clause)

        return stmt

    def parse_select_stmt(self, union_op=None):
        if not self.state.is_reserved('select') and not self.state.is_open_paren():
            return

        if self.state.is_open_paren():
            stmt = self.parse_expr()
        else:
            stmt = self.parse_select_body()

        if self.state.is_reserved('union'):
            union = self.accept(ast.Op, self.state.value)
            union.add_child(stmt)
            next_stmt = self.run()
            if next_stmt:
                union.add_child(next_stmt)
            return union

        return stmt

    def run(self):
        return self.parse_select_stmt()
