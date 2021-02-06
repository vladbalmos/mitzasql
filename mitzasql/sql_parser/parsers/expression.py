# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

# Expressions parser for the following grammar:
# https://dev.mysql.com/doc/refman/8.0/en/expressions.html
#
# expr:
#     expr OR expr
#   | expr || expr
#   | expr XOR expr
#   | expr AND expr
#   | expr && expr
#   | NOT expr
#   | ! expr
#   | boolean_primary IS [NOT] {TRUE | FALSE | UNKNOWN}
#   | boolean_primary
#
# boolean_primary:
#     boolean_primary IS [NOT] NULL
#   | boolean_primary <=> predicate
#   | boolean_primary comparison_operator predicate
#   | boolean_primary comparison_operator {ALL | ANY} (subquery)
#   | predicate
#
# comparison_operator: = | >= | > | <= | < | <> | !=
#
# predicate:
#     bit_expr [NOT] IN (subquery)
#   | bit_expr [NOT] IN (expr [, expr] ...)
#   | bit_expr [NOT] BETWEEN bit_expr AND predicate
#   | bit_expr SOUNDS LIKE bit_expr
#   | bit_expr [NOT] LIKE simple_expr [ESCAPE simple_expr]
#   | bit_expr [NOT] REGEXP bit_expr
#   | bit_expr
#
# bit_expr:
#     bit_expr | bit_expr
#   | bit_expr & bit_expr
#   | bit_expr << bit_expr
#   | bit_expr >> bit_expr
#   | bit_expr + bit_expr
#   | bit_expr - bit_expr
#   | bit_expr * bit_expr
#   | bit_expr / bit_expr
#   | bit_expr DIV bit_expr
#   | bit_expr MOD bit_expr
#   | bit_expr % bit_expr
#   | bit_expr ^ bit_expr
#   | bit_expr + interval_expr
#   | bit_expr - interval_expr
#   | simple_expr
#
# simple_expr:
#     literal
#   | identifier
#   | function_call
#   | simple_expr COLLATE collation_name
#   | param_marker
#   | variable
#   | simple_expr || simple_expr
#   | + simple_expr
#   | - simple_expr
#   | ~ simple_expr
#   | ! simple_expr
#   | BINARY simple_expr
#   | (expr [, expr] ...)
#   | ROW (expr, expr [, expr] ...)
#   | (subquery)
#   | EXISTS (subquery)
#   | {identifier expr}
#   | match_expr
#   | case_expr
#   | interval_expr

from .. import ast
from .. import parser_factory
from .parser import Parser

class ExpressionParser(Parser):

    def __init__(self, state):
        super().__init__(state)

    def parse_identifier(self):
        expr = self.accept(ast.Expression, self.state.value, 'identifier')

        if self.state.is_dot():
            self.state.next()
            expr.add_child(self.parse_identifier())

        return expr

    def parse_binary_operator(self):
        '''
        Parse binary operator expression:
            BINARY simple_expr
        '''
        expr = self.accept(ast.UnaryOp, self.state.value)
        expr.add_child(self.parse_simple_expr())
        return expr

    def parse_interval_expr(self):
        '''
        Parse interval expression:
            interval_expr: INTERVAL expr unit
        '''
        expr = self.accept(ast.Expression, self.state.value, 'interval')
        expr.add_child(self.parse_simple_expr())
        expr.add_child(self.parse_simple_expr())
        return expr

    def parse_match_expr(self):
        '''
        Parse match expression:
            match_expr: MATCH (col1, col2) AGAINST ("string" IN BOOLEAN MODE)
        '''
        expr = self.accept(ast.Expression, self.state.value, 'match')

        expr.add_child(self.parse_paren())

        if not self.state.is_keyword() or self.state.lcase_value != 'against':
            return expr

        against = self.accept(ast.Op, self.state.value)
        expr.add_child(against)

        if not self.state.is_open_paren():
            return expr

        self.state.next()

        against.add_child(self.parse_expr())

        modifier = None
        while self.state and not self.state.is_closed_paren():
            if modifier is None:
                modifier = self.accept(ast.Op, 'modifier', advance=False)

            modifier.add_child(self.parse_expr())

        against.add_child(modifier)

        if self.state.is_closed_paren():
            self.state.next()

        return expr

    def parse_exist_expr(self):
        '''
        Parse exists expression:
            EXISTS (subquery)
        '''

        if not self.state.is_reserved('exists'):
            return

        exists = self.accept(ast.UnaryOp, self.state.value)

        if not self.state.is_subquery():
            return exists

        exists.add_child(self.parse_expr())
        return exists


    def parse_when_expr(self):
        if not self.state.is_reserved('when'):
            return

        op = self.accept(ast.Op, self.state.value)
        op.add_child(self.parse_expr())

        if self.state.is_reserved('then'):
            self.state.next()
            op.add_child(self.parse_expr())

        return op

    def parse_case_expr(self):
        if not self.state.is_operator('case'):
            return

        op = self.accept(ast.Op, self.state.value)

        if not self.state.is_reserved('when'):
            value_expr = self.parse_expr()
            value = self.accept(ast.Expression, type='value', advance=False)
            value.add_child(value_expr)
            op.add_child(value)

        if self.state.is_reserved('when'):
            while self.state and not (self.state.is_keyword('end') or self.state.is_keyword('else')):
                when = self.parse_when_expr()
                op.add_child(when)

            if self.state.is_keyword('else'):
                else_ = self.accept(ast.Op, self.state.value, pos=self.state.pos, advance=False)
                self.state.next()
                else_.add_child(self.parse_expr())
                op.add_child(else_)

            if self.state.is_keyword('end'):
                self.state.next()

        return op

    def parse_paren(self):
        '''
        Parse parenthesized expression:
            (expr [, expr] ...)
        '''
        if not self.state.is_open_paren():
            return

        paren_expr = self.accept(ast.Expression, type='paren_group')
        while self.state and not self.state.is_closed_paren():
            paren_expr.add_child(self.parse_expr())
            if self.state.is_comma():
                self.state.next()

        if self.state.is_closed_paren():
            self.state.next()

        return paren_expr

    def parse_row_subquery(self):
        '''
        Parse row subquery:
            ROW (expr, expr [, expr] ...): ROW (col1, col2)
        '''
        expr = self.accept(ast.Expression, self.state.value, 'row_subquery')

        self.state.next()

        while self.state and not self.state.is_closed_paren():
            expr.add_child(self.parse_expr())
            if self.state.is_comma():
                self.state.next()

        if self.state.is_closed_paren():
            self.state.next()

        return expr

    def parse_function_call(self):
        '''
        Parse function call:
            function_call: LEFT('string')
        '''

        expr = self.accept(ast.Expression, self.state.value, 'function')

        while self.state and not self.state.is_closed_paren():
            self.state.next()
            argument = self.parse_expr()
            expr.add_child(argument)

        self.state.next()
        return expr

    def parse_simple_expr_term(self):
        '''
        Parse simple expression which can contain only unary operators
        '''
        if not self.state or self.state.is_comma():
            return

        tvalue = self.state.lcase_value

        if self.state.is_reserved():
            if tvalue == 'binary':
                return self.parse_binary_operator()

            if tvalue == 'interval':
                return self.parse_interval_expr()

            if tvalue == 'match':
                return self.parse_match_expr()

            if tvalue == 'exists':
                return self.parse_exist_expr()

        if self.state.is_operator('case'):
            return self.parse_case_expr()

        if self.state.is_row_subquery():
            return self.parse_row_subquery()

        if self.state.is_function_call():
            return self.parse_function_call()

        if self.state.is_subquery():
            self.state.next()
            select_stmt_parser = parser_factory.create(parser_factory.SELECT_STMT, self.state)
            subquery = select_stmt_parser.run()
            if subquery is not None:
                self.last_node = select_stmt_parser.last_node

            if self.state.is_closed_paren():
                self.state.next()
            return subquery

        if self.state.is_open_paren():
            return self.parse_paren()

        if self.state.is_closed_paren():
            self.state.next()
            return

        if self.state.is_operator():
            if tvalue in ast.simple_expr_unary_operators:
                expr = self.accept(ast.UnaryOp, tvalue)
                expr.add_child(self.parse_simple_expr())
                return expr

            if self.state.is_operator('*'):
                return self.accept(ast.Op, '*')

        if self.state.is_literal():
            return self.accept(ast.Expression, self.state.value, 'literal')

        if self.state.is_identifier():
            return self.parse_identifier()

        if self.state.is_keyword():
            return self.accept(ast.Expression, self.state.value, 'keyword')

        if self.state.is_variable():
            return self.accept(ast.Expression, self.state.value, 'variable')

        if self.state.is_param_marker():
            return self.accept(ast.Expression, self.state.value, 'param_marker')

        return self.accept(ast.Expression, self.state.value, 'unknown')

    def parse_simple_expr(self):
        expr = None

        while expr is None and self.state:
            expr = self.parse_simple_expr_term()
            if expr is None:
                self.state.next()

        if expr is None:
            return expr

        tvalue = self.state.lcase_value

        if self.state.is_operator('||'):
            op = self.accept(ast.Op, tvalue)
            op.add_child(expr)
            op.add_child(self.parse_simple_expr())
            return op

        if self.state.is_reserved():
            if tvalue == 'collate':
                op = self.accept(ast.Op, tvalue)
                op.add_child(expr)
                if not (self.state.is_other() or self.state.is_literal()):
                    return op
                op.add_child(self.accept(ast.Expression, self.state.value, 'collation'))
                return op

        return expr

    def parse_bit_expr(self, prev_operator=None):
        lexpr = self.parse_simple_expr()
        if not self.state.is_bit_expr_operator():
            if prev_operator:
                prev_operator.add_child(lexpr)
                return prev_operator
            return lexpr

        if lexpr is None:
            return

        tvalue = self.state.lcase_value
        operator = self.accept(ast.Op, tvalue)

        if not prev_operator:
            operator.add_child(lexpr)
            return self.parse_bit_expr(operator)

        if prev_operator.has_precedance(operator):
            prev_operator.add_child(lexpr)
            operator.add_child(prev_operator)
            return self.parse_bit_expr(operator)

        operator.add_child(lexpr)
        prev_operator.add_child(self.parse_bit_expr(operator))
        return prev_operator

    def parse_predicate(self):
        lexpr = self.parse_bit_expr()

        if lexpr is None or not self.state.is_predicate_operator():
            return lexpr

        not_op = None

        if self.state.is_operator('not'):
            not_op = self.accept(ast.Op, self.state.value)

        if self.state.is_reserved('in'):
            in_op = self.accept(ast.Op, self.state.value)
            in_op.add_child(lexpr)
            in_op.add_child(self.parse_expr())

            if not_op:
                not_op.add_child(in_op)
                in_op = not_op
            return in_op


        if self.state.is_operator('sounds'):
            op = self.accept(ast.Op, self.state.value)
            op.add_child(lexpr)

            if self.state.is_operator('like'):
                like_op = self.accept(ast.Op, self.state.value)
                like_op.add_child(self.parse_bit_expr())
                op.add_child(like_op)
            return op

        if self.state.is_operator('regexp'):
            op = self.accept(ast.Op, self.state.value)
            op.add_child(lexpr)
            rexpr = self.parse_bit_expr()

            if not_op:
                not_op.add_child(rexpr)
                rexpr = not_op
            op.add_child(rexpr)
            return op

        if self.state.is_operator('like'):
            op = self.accept(ast.Op, self.state.value)
            op.add_child(lexpr)
            rexpr = self.parse_simple_expr()

            escape_op = None
            if self.state.is_keyword('escape'):
                escape_op_value = self.state.lcase_value
                escape_op = self.accept(ast.Op, escape_op_value)
                escape_op.add_child(self.parse_simple_expr())

            if not_op:
                not_op.add_child(rexpr)
                rexpr = not_op

            op.add_child(rexpr)
            if escape_op:
                op.add_child(escape_op)
            return op

        if self.state.is_operator('between'):
            op = self.accept(ast.Op, self.state.value)
            op.add_child(lexpr)

            range = self.accept(ast.Expression, type='range', pos=self.state.pos, advance=False)
            range.add_child(self.parse_bit_expr())

            if self.state.is_operator('and'):
                self.state.next()
                range.add_child(self.parse_predicate())

            if not_op:
                not_op.add_child(range)
                range = not_op
            op.add_child(range)
            return op

        return lexpr

    def parse_boolean_primary(self, lexpr=None):
        if lexpr is None:
            lexpr = self.parse_predicate()

        if not self.state.is_bool_primary_operator() or lexpr is None:
            return lexpr

        tvalue = self.state.lcase_value

        operator = self.accept(ast.Op, tvalue)
        operator.add_child(lexpr)

        if tvalue == 'is':
            if self.state.is_operator('not'):
                not_op = self.accept(ast.UnaryOp, 'not')

                if self.state.is_literal('null'):
                    not_op.add_child(self.accept(ast.Expression, 'null', 'literal'))

                operator.add_child(not_op)
            elif self.state.is_literal('null'):
                operator.add_child(self.accept(ast.Expression, 'null', 'literal'))
        else:
            modifier_op = None
            if self.state.lcase_value in ('any', 'all'):
                modifier_op = self.accept(ast.UnaryOp, self.state.value)

            predicate = self.parse_predicate()

            if modifier_op:
                modifier_op.add_child(predicate)
                predicate = modifier_op

            operator.add_child(predicate)

        if self.state.is_bool_primary_operator():
            return self.parse_boolean_primary(operator)

        return operator

    def parse_expr_term(self, lexpr=None):
        if self.state.is_expression_operator() and (self.state.lcase_value == '!' or self.state.lcase_value == 'not'):
            expr = self.accept(ast.UnaryOp, self.state.lcase_value)
            expr.add_child(self.parse_expr())
            return expr

        if lexpr is None:
            lexpr = self.parse_boolean_primary()
            if lexpr is None:
                return

        if not self.state.is_expression_operator() or not self.state.is_operator('is'):
            return lexpr

        tvalue = self.state.lcase_value

        operator = self.accept(ast.Op, tvalue)
        operator.add_child(lexpr)

        if self.state.is_operator('not'):
            not_op = self.accept(ast.UnaryOp, 'not')

            if self.state.lcase_value in ['true', 'false', 'unknown']:
                not_op.add_child(self.accept(ast.Expression, self.state.lcase_value, 'literal'))

            operator.add_child(not_op)
        elif self.state.lcase_value in ['true', 'false', 'unknown']:
            operator.add_child(self.accept(ast.Expression, self.state.lcase_value, 'literal'))

        return operator

    def parse_expr(self, prev_operator=None):
        lexpr = self.parse_expr_term()
        if not self.state.is_expression_operator() or self.state.is_operator('not') or self.state.is_operator('!'):
            if prev_operator:
                prev_operator.add_child(lexpr)
                return prev_operator
            return lexpr

        tvalue = self.state.lcase_value

        operator = self.accept(ast.Op, self.state.lcase_value)

        if tvalue == 'is':
            return self.parse_expr_term(lexpr)

        if not prev_operator:
            operator.add_child(lexpr)
            return self.parse_expr(operator)

        if prev_operator.has_precedance(operator):
            prev_operator.add_child(lexpr)
            operator.add_child(prev_operator)
            return self.parse_expr(operator)

        operator.add_child(lexpr)
        prev_operator.add_child(self.parse_expr(operator))
        return prev_operator

    def run(self):
        return self.parse_expr()

