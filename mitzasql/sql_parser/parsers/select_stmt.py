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

        self.table_terminator_keywords = self.col_terminator_keywords[1:]

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

    def is_table_reference(self, state=None):
        if state is None:
            state = self.state
        if state.is_literal() or state.is_name() or state.is_other():
            return True

        if not (state.is_keyword() or state.is_function() or state.is_open_paren):
            return False

        terminator_keywords = self.table_terminator_keywords + ('partition',
                'as', 'inner', 'cross', 'join', 'straight_join', 'on', 'left',
                'right', 'outer', 'natural', 'using', 'use', 'index', 'key',
                'ignore', 'force', 'index', 'key', 'for')

        return state.lcase_value not in terminator_keywords

    def is_table_alias(self):
        if self.state.is_reserved('as'):
            return True

        if self.state.is_literal() or self.state.is_name() or self.state.is_other():
            return True

        return self.is_table_reference()

        with self.state as future_state:
            future_state.next()
            val = self.is_table_reference(future_state)
            return val

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

    def parse_table_partition(self):
        if not self.state.is_reserved('partition'):
            return

        partition = self.accept(ast.UnaryOp, self.state.value)
        partition.add_child(self.expr_parser.parse_expr())
        return partition

    def parse_table_index_hint(self):
        if not self.state.is_reserved() or self.state.lcase_value not in ('use', 'ignore', 'force', 'index', 'key'):
            return

        index_hint = ast.Expression(type='index_hint')

        def parse_for(parent):
            if not self.state.is_reserved('for'):
                return

            for_ = self.accept(ast.UnaryOp, self.state.value)
            if self.state.is_reserved() and self.state.lcase_value in ('join', 'order', 'group'):
                if self.state.is_reserved('join'):
                    for_.add_child(self.accept(ast.Expression, self.state.value))
                else:
                    expr = self.accept(ast.UnaryOp, self.state.value)
                    if self.state.is_reserved('by'):
                        expr.add_child(self.accept(ast.UnaryOp, self.state.value))
                    for_.add_child(expr)
            parent.add_child(for_)

        if self.state.is_reserved('use'):
            use = self.accept(ast.UnaryOp, self.state.value)
            index_hint.add_child(use)
            if self.state.is_reserved('index') or self.state.is_reserved('key'):
                use.add_child(self.accept(ast.Expression, self.state.value))

            parse_for(use)

            if self.state.is_open_paren():
                use.add_child(self.expr_parser.parse_expr())

            return index_hint

        expr = None
        if self.state.lcase_value in ('ignore', 'force'):
            expr = self.accept(ast.UnaryOp, self.state.value)
            index_hint.add_child(expr)

        if self.state.lcase_value in ('index', 'key'):
            expr_ = self.accept(ast.UnaryOp, self.state.value)
            if expr is not None:
                expr.add_child(expr_)

        parse_for(index_hint)

        if self.state.is_open_paren():
            index_hint.add_child(self.expr_parser.parse_expr())

        return index_hint

    def parse_join_spec(self, spec):
        if not self.state.is_reserved(spec):
            return
        op = self.accept(ast.UnaryOp, self.state.value)
        op.add_child(self.expr_parser.parse_expr())
        return op

    def parse_join(self, parse_outer=False, parse_dir=True, parse_table_factor=True):
        if parse_dir and self.state.lcase_value in ('left', 'right'):
            join = self.accept(ast.UnaryOp, self.state.value)
            join.add_child(self.parse_join(parse_outer=True, parse_dir=False, parse_table_factor=parse_table_factor))
            return join

        if parse_outer and self.state.is_reserved('outer'):
            outer = self.accept(ast.UnaryOp, self.state.value)
            outer.add_child(self.parse_join(parse_outer=False, parse_dir=False, parse_table_factor=parse_table_factor))
            return outer

        if self.state.is_reserved('join'):
            join = self.accept(ast.UnaryOp, self.state.value)
            if not parse_table_factor:
                join.add_child(self.parse_table_reference())
            else:
                join.add_child(self.parse_table_factor())

            if self.state.is_reserved('on'):
                join.add_child(self.parse_join_spec('on'))

            if self.state.is_reserved('using'):
                join.add_child(self.parse_join_spec('using'))
            return join

    def parse_table_factor(self):
        if not self.is_table_reference():
            return

        table_factor = None
        if self.state.is_open_paren():
            self.state.next()
            table_factor = ast.Expression(type='table_reference')
            while self.state and not self.state.is_closed_paren():
                table_factor.add_child(self.parse_table_reference())
                if self.state.is_comma():
                    self.state.next()

            if self.state.is_closed_paren():
                self.state.next()

        if table_factor is None:
            table_factor = ast.Expression(type='table_reference')

        if self.state.is_reserved('select'):
            table_factor.add_child(self.parse_select_stmt())
        else:
            table_factor.add_child(self.accept(ast.Expression, self.state.value))

        if self.state.is_reserved('partition'):
            table_factor.add_child(self.parse_table_partition())

        if self.is_table_alias():
            table_factor.add_child(self.parse_alias())

        while self.state and self.state.is_reserved() and self.state.lcase_value in ('use', 'ignore', 'force', 'index', 'key'):
            table_factor.add_child(self.parse_table_index_hint())
            if self.state.is_comma():
                self.state.next()

        return table_factor

    def parse_table_reference(self, table_factor=None):
        if table_factor is None:
            table_factor = self.parse_table_factor()
            if table_factor is None:
                return

        if not self.state.is_reserved() and not self.state.is_function():
            return table_factor

        if self.state.lcase_value not in ('inner', 'cross', 'straight_join', 'left', 'right', 'outer', 'natural', 'join'):
            return table_factor

        if self.state.is_reserved('straight_join'):
            join = self.accept(ast.UnaryOp, self.state.value)
            join.add_child(self.parse_table_factor())

            if self.state.is_reserved('on'):
                join.add_child(self.parse_join_spec('on'))

            table_factor.add_child(join)
            return self.parse_table_reference(table_factor)

        if self.state.is_reserved('inner') or self.state.is_reserved('cross'):
            join_op = self.accept(ast.UnaryOp, self.state.value)
            join_op.add_child(self.parse_join(parse_outer=False, parse_dir=False))
            table_factor.add_child(join_op)
            return self.parse_table_reference(table_factor)

        if self.state.is_reserved('natural'):
            natural_op = self.accept(ast.UnaryOp, self.state.value)
            natural_op.add_child(self.parse_join(parse_outer=True))
            table_factor.add_child(natural_op)
            return self.parse_table_reference(table_factor)

        if self.state.is_reserved() or self.state.is_function():
            if self.state.lcase_value in ('inner', 'cross', 'straight_join', 'left', 'right', 'outer', 'natural', 'join'):
                table_factor.add_child(self.parse_join(parse_outer=True, parse_dir=True, parse_table_factor=False))

        table_factor = self.parse_table_reference(table_factor)

        return table_factor

    def parse_from(self):
        if not self.state.is_reserved('from'):
            return

        from_clause = self.accept(ast.Expression, type='from')

        while self.state and self.is_table_reference():
            from_clause.add_child(self.parse_table_reference())
            if self.state.is_comma():
                self.state.next()

        return from_clause

    def parse_where(self):
        if not self.state.is_reserved('where'):
            return

        where_clause = self.accept(ast.Expression, type='where')
        where_clause.add_child(self.expr_parser.parse_expr())
        return where_clause

    def parse_order_expr(self):
        expr = self.expr_parser.parse_expr()
        if expr is None:
            return

        if self.state.is_reserved() and self.state.lcase_value in ('asc', 'desc'):
            order_op = self.accept(ast.UnaryOp, self.state.value)
            order_op.add_child(expr)
            return order_op

        return expr

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
        where_clause.add_child(self.expr_parser.parse_expr())
        return where_clause

    def parse_order_by(self):
        if not self.state.is_reserved('order'):
            return

        order = self.accept(ast.Op, self.state.value)

        if not self.state.is_reserved('by'):
            return order

        by = self.accept(ast.Op, self.state.value)
        order.add_child(by)

        while self.state:
            expr = self.parse_order_expr()
            if expr is None:
                break
            by.add_child(expr)

            if self.state.is_comma():
                self.state.next()
                continue
            break

        return order

    def parse_limit(self):
        if not self.state.is_reserved('limit'):
            return

        offset = quantity = None
        limit = self.accept(ast.Op, self.state.value)
        # pudb.set_trace()

        val = self.expr_parser.parse_expr()
        if val is None:
            return limit

        if self.state.is_keyword('offset'):
            self.state.next()
            quantity = val
            offset = self.expr_parser.parse_expr()
        elif self.state.is_comma():
            self.state.next()
            offset = val
            quantity = self.expr_parser.parse_expr()
        else:
            quantity = val

        limit.add_child(offset)
        limit.add_child(quantity)
        return limit

    def parse_procedure(self):
        if not self.state.is_reserved('procedure'):
            return

        procedure = self.accept(ast.UnaryOp, self.state.value)
        if self.state.is_function_call():
            procedure.add_child(self.expr_parser.parse_expr())

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

    def parse_select_stmt(self, union_op=None):
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

        if self.state.is_reserved('union'):
            if union_op is not None:
                self.state.next()
            else:
                union = self.accept(ast.Op, self.state.value)
                union.add_child(stmt)

                while self.state and not self.state.is_semicolon():
                    union.add_child(self.parse_select_stmt(union))
                return union

        return stmt

    def run(self):
        return self.parse_select_stmt()
