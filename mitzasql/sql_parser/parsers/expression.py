import pudb
import mitzasql.sql_parser.tokens as Token
import mitzasql.sql_parser.ast as ast
import mitzasql.sql_parser.parser_factory as parser_factory

class ExpressionParser:

    def __init__(self, state):
        self.state = state

    def parse_collation(self):
        if not self.state.is_other():
            return

        expr = ast.Expression(self.state.value, 'collation')
        self.state += 1
        return expr

    def parse_identifier(self, allowed_types=[Token.Name]):
        if self.state.type not in allowed_types:
            return

        expr = ast.Expression(self.state.value, 'identifier')
        self.state += 1

        if self.state.is_dot():
            self.state += 1
            expr.add_child(self.parse_identifier())

        return expr

    def parse_binary_expr(self):
        expr = ast.UnaryOp(self.state.value)
        self.state += 1
        expr.add_child(self.parse_simple_expr())
        return expr

    def parse_interval_expr(self):
        expr = ast.Expression(self.state.value, 'interval')
        self.state += 1
        expr.add_child(self.parse_simple_expr())
        expr.add_child(self.parse_simple_expr())
        return expr

    def parse_match_expr(self):
        expr = ast.Expression(self.state.value, 'match')
        self.state += 1
        expr.add_child(self.parse_paren())

        if not self.state:
            return expr

        if not self.state.is_keyword() or self.state.lcase_value != 'against':
            return expr

        against = ast.Op(self.state.value)
        expr.add_child(against)
        self.state += 1

        if not self.state.is_open_paren():
            return expr

        self.state += 1

        against.add_child(self.parse_expr())

        modifier = None
        while self.state and not self.state.is_closed_paren():
            if modifier is None:
                modifier = ast.Op('modifier')

            modifier.add_child(self.parse_expr())

        against.add_child(modifier)

        if self.state.is_closed_paren():
            self.state += 1

        return expr

    def parse_paren(self):
        self.state += 1
        paren_expr = ast.Expression(type='paren_group')
        while self.state and not self.state.is_closed_paren():
            paren_expr.add_child(self.parse_expr())
            if self.state.is_comma():
                self.state += 1

        if self.state.is_closed_paren():
            self.state += 1

        return paren_expr

    def parse_row_subquery(self):
        expr = ast.Expression(self.state.value, 'row_subquery')
        self.state += 1

        expr.add_child(self.parse_paren())
        return expr

    def parse_function_call(self):
        expr = ast.Expression(self.state.value, 'function')
        self.state += 1

        while self.state and not self.state.is_closed_paren():
            argument = self.parse_expr()
            expr.add_child(argument)

        self.state += 1
        return expr

    def parse_simple_expr_term(self):
        if not self.state or self.state.is_comma():
            return

        tvalue = self.state.lcase_value

        if self.state.is_reserved():
            if tvalue == 'binary':
                return self.parse_binary_expr()

            if tvalue == 'interval':
                return self.parse_interval_expr()

            if tvalue == 'match':
                return self.parse_match_expr()

            # TODO: fix this
            if tvalue == 'case':
                return self.parse_case_expr()


        if self.state.is_row_subquery():
            return self.parse_row_subquery()

        if self.state.is_function_call():
            return self.parse_function_call()

        if self.state.is_open_paren():
            return self.parse_paren()

        if self.state.is_closed_paren():
            self.state += 1
            return

        if self.state.is_operator():
            if tvalue in ast.simple_expr_unary_operators:
                self.state += 1
                expr = ast.UnaryOp(tvalue)
                expr.add_child(self.parse_simple_expr())
                return expr

            if self.state.is_operator('*'):
                self.state += 1
                return ast.Op('*')

        if self.state.is_literal():
            expr = ast.Expression(self.state.value, 'literal')
            self.state += 1
            return expr

        if self.state.is_name():
            return self.parse_identifier()

        if self.state.is_keyword():
            expr = ast.Expression(self.state.value, 'keyword')
            self.state += 1
            return expr

        if self.state.is_variable():
            expr = ast.Expression(self.state.value, 'variable')
            self.state += 1
            return expr

        if self.state.is_param_marker():
            expr = ast.Expression(self.state.value, 'param_marker')
            self.state += 1
            return expr

        expr = ast.Expression(self.state.value, 'unknown')
        self.state += 1
        return expr

    def parse_simple_expr(self):
        expr = None

        while expr is None and self.state:
            expr = self.parse_simple_expr_term()
            if expr is None:
                self.state += 1

        if expr is None:
            return expr

        tvalue = self.state.lcase_value

        if self.state.is_operator('||'):
            self.state += 1
            op = ast.Op(tvalue)
            op.add_child(expr)
            op.add_child(self.parse_simple_expr())
            return op

        if self.state.is_reserved():
            if tvalue == 'collate':
                self.state += 1
                op = ast.Op(tvalue)
                op.add_child(expr)
                op.add_child(self.parse_collation())
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
        self.state +=1

        operator = ast.Op(tvalue)

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

    def parse_predicate(self, lexpr = None):
        if lexpr is None:
            lexpr = self.parse_bit_expr()

        if lexpr is None:
            return lexpr

        tvalue = self.state.lcase_value

        if self.state.is_operator():
            if self.state.is_operator('not'):
                self.state += 1
                op = ast.UnaryOp(tvalue)
                op.add_child(self.parse_predicate(lexpr))
                return op

            if self.state.is_operator('sounds'):
                self.state += 1
                op = ast.Op(tvalue)
                op.add_child(lexpr)

                if self.state.is_operator('like'):
                    self.state += 1
                    like_op = ast.Op(self.state.lcase_value)
                    like_op.add_child(self.parse_bit_expr())
                    op.add_child(like_op)
                return op

            if self.state.is_operator('regexp'):
                self.state += 1
                op = ast.Op(tvalue)
                op.add_child(lexpr)
                op.add_child(self.parse_bit_expr())
                return op

            if self.state.is_operator('like'):
                self.state += 1
                op = ast.Op(tvalue)
                op.add_child(lexpr)
                op.add_child(self.parse_simple_expr())

                if self.state.is_keyword('escape'):
                    escape_op_value = self.state.lcase_value
                    self.state += 1
                    escape_op = ast.Op(escape_op_value)
                    escape_op.add_child(self.parse_simple_expr())
                    op.add_child(escape_op)
                return op

            if self.state.is_operator('between'):
                self.state += 1
                op = ast.Op(tvalue)
                op.add_child(lexpr)
                op.add_child(self.parse_bit_expr())

                if self.state.is_operator('and'):
                    self.state += 1
                    op.add_child(self.parse_predicate())
                return op

        return lexpr

    def parse_boolean_primary(self, lexpr=None):
        if lexpr is None:
            lexpr = self.parse_predicate()

        if not self.state.is_bool_primary_operator() or lexpr is None:
            return lexpr

        tvalue = self.state.lcase_value
        self.state += 1

        operator = ast.Op(tvalue)
        operator.add_child(lexpr)

        if tvalue == 'is':
            if self.state.is_operator('not'):
                not_op = ast.UnaryOp('not')
                self.state += 1

                if self.state.is_literal('null'):
                    self.state += 1
                    not_op.add_child(ast.Expression('null', 'literal'))

                operator.add_child(not_op)
            elif self.state.is_literal('null'):
                self.state += 1
                operator.add_child(ast.Expression('null', 'literal'))
        else:
            operator.add_child(self.parse_predicate())

        if self.state.is_bool_primary_operator():
            return self.parse_boolean_primary(operator)

        return operator

    def parse_expr_term(self, lexpr=None):
        if self.state.is_expression_operator() and (self.state.lcase_value == '!' or self.state.lcase_value == 'not'):
            expr = ast.UnaryOp(self.state.lcase_value)
            self.state += 1
            expr.add_child(self.parse_expr())
            return expr

        if lexpr is None:
            lexpr = self.parse_boolean_primary()
            if lexpr is None:
                return

        if not self.state.is_expression_operator() or not self.state.is_operator('is'):
            return lexpr

        tvalue = self.state.lcase_value
        self.state += 1

        operator = ast.Op(tvalue)
        operator.add_child(lexpr)

        if self.state.is_operator('not'):
            not_op = ast.UnaryOp('not')
            self.state += 1

            if self.state.lcase_value in ['true', 'false', 'unknown']:
                not_op.add_child(ast.Expression(self.state.lcase_value, 'literal'))
                self.state += 1

            operator.add_child(not_op)
        elif self.state.lcase_value in ['true', 'false', 'unknown']:
            operator.add_child(ast.Expression(self.state.lcase_value, 'literal'))
            self.state += 1

        return operator

    def parse_expr(self, prev_operator=None):
        lexpr = self.parse_expr_term()
        if not self.state.is_expression_operator():
            if prev_operator:
                prev_operator.add_child(lexpr)
                return prev_operator
            return lexpr

        if lexpr is None:
            return

        tvalue = self.state.lcase_value
        self.state += 1

        operator = ast.Op(tvalue)

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

