import mitzasql.sql_parser.ast as ast
import mitzasql.sql_parser.parser_factory as parser_factory
from mitzasql.sql_parser.parsers.parser import Parser

SELECT_MODIFIER_KW = ('all', 'distinct', 'distinctrow',
        'high_priority', 'straight_join', 'sql_small_result',
        'sql_big_result', 'sql_buffer_result', 'sql_cache',
        'sql_no_cache', 'sql_calc_found_rows')

COL_TERMINATOR_KEYWORDS = ('from', 'where', 'group',
        'having', 'order', 'limit', 'procedure', 'for', 'into', 'lock',
        'union')

TABLE_TERMINATOR_KEYWORDS = COL_TERMINATOR_KEYWORDS[1:] + ('partition',
        'as', 'inner', 'cross', 'join', 'straight_join', 'on',
        'left', 'right', 'outer', 'natural', 'using',
        'use', 'index', 'key', 'ignore', 'force', 'index', 'key', 'for')

class SelectStmtParser(Parser):
    def __init__(self, state):
        super().__init__(state)
        self.expr_parser = parser_factory.create(parser_factory.EXPR, state)

    def is_select_modifier(self):
        if not self.state:
            return False

        if not self.state.is_keyword():
            return False

        return self.state.lcase_value in SELECT_MODIFIER_KW

    def is_select_expr(self):
        if not self.state:
            return False

        if self.state.is_literal() or self.state.is_name() or self.state.is_other():
            return True

        return self.state.lcase_value not in COL_TERMINATOR_KEYWORDS

    def is_subquery_table_reference(self):
        if not self.state:
            return False

        if not self.state.is_open_paren():
            return False

        with self.state as future_state:
            future_state.next()
            return future_state.is_reserved('select')

    def is_table_reference(self, state=None):
        if state is None:
            state = self.state

        if not state:
            return False

        if state.is_literal() or state.is_name() or state.is_other():
            return True

        if not (state.is_keyword() or state.is_function() or state.is_open_paren()):
            return False

        return state.lcase_value not in TABLE_TERMINATOR_KEYWORDS

    def is_table_alias(self):
        if not self.state:
            return False

        if self.state.is_reserved('as'):
            return True

        if not (self.state.lcase_value.isalnum() and not self.state.lcase_value.isnumeric()):
            return False

        if self.state.lcase_value in TABLE_TERMINATOR_KEYWORDS:
            return False

        if self.state.is_literal() or self.state.is_name() or self.state.is_other():
            return True

        with self.state as future_state:
            future_state.next()
            val = self.is_table_reference(future_state)
            return val

    def parse_expr(self):
        expr = self.expr_parser.parse_expr()
        if expr is not None:
            self.last_node = self.expr_parser.last_node
        return expr

    def parse_alias(self):
        if self.state.is_reserved('as'):
            self.state.next()
        expr = self.parse_expr()

        if expr is None:
            return

        alias = self.accept(ast.Expression, type='alias', advance=False)
        alias.add_child(expr)
        return alias

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
        partition.add_child(self.parse_expr())
        return partition

    def parse_table_index_hint(self):
        if not self.state.is_reserved() or self.state.lcase_value not in ('use', 'ignore', 'force', 'index', 'key'):
            return

        index_hint = self.accept(ast.Expression, type='index_hint', advance=False)

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
                use.add_child(self.parse_expr())

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
            index_hint.add_child(self.parse_expr())

        return index_hint

    def parse_join_spec(self, spec):
        if not self.state.is_reserved(spec):
            return
        op = self.accept(ast.Expression, self.state.value, spec)
        op.add_child(self.parse_expr())
        return op

    def parse_join(self, parse_outer=False, parse_dir=True):
        join = None
        join_expr = None
        join_spec = None

        if parse_dir and self.state.lcase_value in ('left', 'right'):
            join = self.accept(ast.Expression, self.state.value, 'join_dir')
            join_expr = self.parse_join(parse_outer=True, parse_dir=False)

        if parse_outer and self.state.is_reserved('outer'):
            join = self.accept(ast.Expression, self.state.value, 'join_type')
            join_expr = self.parse_join(parse_outer=False, parse_dir=False)

        if self.state.is_reserved('join'):
            join = self.accept(ast.Expression, self.state.value, 'join')
            join_expr = self.parse_table_reference()

            if self.state.is_reserved('on'):
                join_spec = self.parse_join_spec('on')

            if self.state.is_reserved('using'):
                join_spec = self.parse_join_spec('using')

        if join:
            if join_expr:
                self.parse_table_reference(join_expr)
                join.add_child(join_expr)

            if join_spec:
                join.add_child(join_spec)

        return join

    def parse_table_factor(self):
        if not self.is_table_reference():
            return

        if self.state.is_open_paren() and not self.is_subquery_table_reference():
            paren_factor = self.accept(ast.Expression, type='table_reference')
            while self.state and not self.state.is_closed_paren():
                child_factor = self.parse_table_reference()
                if child_factor:
                    paren_factor.add_child(child_factor)

                if self.state.is_comma():
                    self.state.next()

            if self.state.is_closed_paren():
                self.state.next()
            return paren_factor

        if self.state.is_closed_paren():
            return

        factor = None

        if self.is_subquery_table_reference():
            factor = self.accept(ast.Expression, type='table_reference', advance=False)
            factor.add_child(self.parse_expr())
        elif self.state:
            factor = self.accept(ast.Expression, type='table_reference', advance=False)
            expr = self.parse_expr()
            if expr:
                factor.add_child(expr)

        if not self.state:
            return factor

        if self.state.is_reserved('partition'):
            factor.add_child(self.parse_table_partition())

        if self.is_table_alias():
            factor.add_child(self.parse_alias())

        while self.state and self.state.is_reserved() and self.state.lcase_value in ('use', 'ignore', 'force', 'index', 'key'):
            factor.add_child(self.parse_table_index_hint())
            if self.state.is_comma():
                self.state.next()

        return factor


    def parse_table_reference(self, table_factor=None):
        if table_factor is None:
            table_factor = self.parse_table_factor()
            if table_factor is None:
                return table_factor

        if not self.state.is_reserved() and not self.state.is_function():
            return table_factor

        if self.state.lcase_value not in ('inner', 'cross', 'straight_join', 'left', 'right', 'outer', 'natural', 'join'):
            return table_factor

        if self.state.is_reserved('straight_join'):
            join = self.accept(ast.Expression, self.state.value, 'join')
            table_ref = self.parse_table_reference()
            if table_ref:
                join.add_child(table_ref)

            if self.state.is_reserved('on'):
                join_spec = self.parse_join_spec('on')
                if join_spec:
                    join.add_child(join_spec)

            table_factor.add_child(join)

        if self.state.is_reserved('inner') or self.state.is_reserved('cross'):
            join = self.accept(ast.Expression, self.state.value, 'join_type')
            join_expr = self.parse_join(parse_outer=False, parse_dir=False)
            if join_expr:
                join.add_child(join_expr)
            table_factor.add_child(join)

        if self.state.is_reserved('natural'):
            join = self.accept(ast.Expression, self.state.value, 'join_type')
            join_expr = self.parse_join(parse_outer=True)
            if join_expr:
                join.add_child(join_expr)
            table_factor.add_child(join)

        if self.state.is_reserved() or self.state.is_function():
            if self.state.lcase_value in ('left', 'right', 'join'):
                join_expr = self.parse_join(parse_outer=True, parse_dir=True)
                if join_expr:
                    table_factor.add_child(join_expr)

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
        where_clause.add_child(self.parse_expr())
        return where_clause

    def parse_order_expr(self):
        expr = self.parse_expr()
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
        where_clause.add_child(self.parse_expr())
        return where_clause

    def parse_order_by(self):
        if not self.state.is_reserved('order'):
            return

        order = self.accept(ast.Expression, type='order')

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

        val = self.parse_expr()
        if val is None:
            return limit

        if self.state.is_keyword('offset'):
            self.state.next()
            quantity = val
            offset = self.parse_expr()
        elif self.state.is_comma():
            self.state.next()
            offset = val
            quantity = self.parse_expr()
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

        if self.is_select_modifier():
            modifier = self.accept(ast.Expression, type='modifier', advance=False)

            while self.state and self.is_select_modifier():
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
            next_stmt = self.parse_select_stmt()
            if next_stmt:
                union.add_child(next_stmt)
            return union

        return stmt

    def run(self):
        return self.parse_select_stmt()
