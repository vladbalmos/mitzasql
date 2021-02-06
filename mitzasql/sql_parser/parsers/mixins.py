# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

from .. import ast
from .. import parser_factory

COL_TERMINATOR_KEYWORDS = ('from', 'where', 'group',
        'having', 'order', 'limit', 'procedure', 'for', 'into', 'lock',
        'union')

TABLE_TERMINATOR_KEYWORDS = COL_TERMINATOR_KEYWORDS + ('partition',
        'as', 'inner', 'cross', 'join', 'straight_join', 'on',
        'left', 'right', 'outer', 'natural', 'using', 'set',
        'use', 'index', 'key', 'ignore', 'force', 'index', 'key', 'for',
        'values', 'value', 'duplicate', 'update', 'select')

class ExprParserMixin():
    def parse_expr(self):
        expr = self.expr_parser.run()
        if expr is not None:
            self.last_node = self.expr_parser.last_node
        return expr

class DMSParserMixin():
    def is_table_reference(self, state=None):
        if state is None:
            state = self.state

        if not state or state.is_semicolon():
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

    def is_subquery_table_reference(self):
        if not self.state:
            return False

        if not self.state.is_open_paren():
            return False

        with self.state as future_state:
            future_state.next()
            return future_state.is_reserved('select')

    def parse_alias(self):
        if self.state.is_reserved('as'):
            self.state.next()
        expr = self.parse_expr()

        if expr is None:
            return

        alias = self.accept(ast.Expression, type='alias', advance=False)
        alias.add_child(expr)
        return alias


    def parse_table_partition(self):
        if not self.state.is_reserved('partition'):
            return

        partition = self.accept(ast.Expression, self.state.value, type='partition')
        partition.add_child(self.parse_expr())
        return partition

    def parse_table_index_hint(self):
        if not self.state.is_reserved() or self.state.lcase_value not in ('use', 'ignore', 'force', 'index', 'key'):
            return

        index_hint = self.accept(ast.Expression, type='index_hint', advance=False)

        def parse_for(parent):
            if not self.state.is_reserved('for'):
                return

            for_ = self.accept(ast.Expression, self.state.value, type='for')
            if self.state.is_reserved() and self.state.lcase_value in ('join', 'order', 'group'):
                if self.state.is_reserved('join'):
                    for_.add_child(self.accept(ast.Expression, self.state.value))
                else:
                    expr = self.accept(ast.Expression, self.state.value, type=self.state.lcase_value)
                    if self.state.is_reserved('by'):
                        expr.add_child(self.accept(ast.Expression, self.state.value, type='by'))
                    for_.add_child(expr)
            parent.add_child(for_)

        if self.state.is_reserved('use'):
            use = self.accept(ast.Expression, self.state.value, type='user')
            index_hint.add_child(use)
            if self.state.is_reserved('index') or self.state.is_reserved('key'):
                use.add_child(self.accept(ast.Expression, self.state.value))

            parse_for(use)

            if self.state.is_open_paren():
                use.add_child(self.parse_expr())

            return index_hint

        expr = None
        if self.state.lcase_value in ('ignore', 'force'):
            expr = self.accept(ast.Expression, self.state.value, type=self.state.lcas)
            if expr:
                index_hint.add_child(expr)

        if self.state.lcase_value in ('index', 'key'):
            expr_ = self.accept(ast.Expression, self.state.value, type=self.state.lcase_value)
            if expr is not None:
                expr.add_child(expr_)

        parse_for(index_hint)

        if self.state.is_open_paren():
            index_hint.add_child(self.parse_expr())

        return index_hint

    def parse_join_spec(self, spec):
        if not self.state.is_reserved(spec):
            return
        op = self.accept(ast.Expression, self.state.value, 'join_spec')
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

    def parse_assignment_list(self):
        pass

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
            order_op = self.accept(ast.Expression, self.state.value, 'order_dir')
            order_op.add_child(expr)
            return order_op

        return expr


    def parse_order_by(self):
        if not self.state.is_reserved('order'):
            return

        order = self.accept(ast.Expression, type='order')

        if not self.state.is_reserved('by'):
            return order

        by = self.accept(ast.Expression, self.state.value, type='by')
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
        limit = self.accept(ast.Expression, self.state.value, type='limit')

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


