import pudb
import mitzasql.sql_parser.tokens as Token
import mitzasql.sql_parser.ast as ast
import mitzasql.sql_parser.parser_factory as parser_factory

class SelectStmtParser:
    def __init__(self, state):
        self.state = state
        self.expr_parser = parser_factory.create(parser_factory.EXPR, state)
        self.select_modifier_kw = ('all', 'distinct', 'distinctrow',
                'high_priority', 'straight_join', 'sql_small_result',
                'sql_big_result', 'sql_buffer_result', 'sql_cache',
                'sql_no_cache', 'sql_calc_found_rows')
        self.col_terminator_keywords = ('from', 'where', 'group',
                'having', 'order', 'limit', 'procedure', 'for', 'into', 'lock',
                'union')

    def accept(self, cls, *args, **kwargs):
        node = cls(*args, **kwargs)
        self.state.next()
        return node

    def is_select_modifier(self):
        if not self.state.is_keyword():
            return False

        return self.state.lcase_value in self.select_modifier_kw

    def is_select_expr(self):
        if self.state.is_literal() or self.state.is_name() or self.state.is_other():
            return True

        return self.state.lcase_value not in self.col_terminator_keywords

    def parse_alias(self):
        if self.state.is_reserved('as'):
            self.state.next()
        expr = self.expr_parser.parse_expr()
        alias = ast.Expression(type='alias')
        alias.add_child(expr)
        return alias

    def parse_col(self):
        col  = ast.Expression(type='column')
        expr = self.expr_parser.parse_expr()

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

        charset = self.accept(ast.UnaryOp, self.state.value)

        if not self.state.is_reserved('set'):
            return charset

        set = self.accept(ast.UnaryOp, self.state.value)
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

            by = self.accept(ast.UnaryOp, self.state.value)

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
        return

    def parse_group_by(self):
        return

    def parse_having(self):
        return

    def parse_order_by(self):
        return

    def parse_limit(self):
        return

    def parse_procedure(self):
        return

    def parse_for_clause(self):
        return

    def parse_lock_clause(self):
        return

    def parse_select_stmt(self):
        if not self.state.is_reserved('select'):
            return

        stmt = self.accept(ast.Statement, self.state.value, 'select')

        if self.is_select_modifier():
            modifier = ast.Expression(type='modifier')

            while self.state and self.is_select_modifier():
                modifier.add_child(self.accept(ast.Expression, self.state.value))

            stmt.add_child(modifier)

        columns = ast.Expression(type='columns')
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

    def run(self):
        return self.parse_select_stmt()
