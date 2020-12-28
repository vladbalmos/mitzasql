from collections import deque
import mitzasql.sql_parser.ast as ast
import mitzasql.sql_parser.tokens as Token

class State:
    def __init__(self, tokens, future=False):
        self._tokens = tokens
        self.lookahead_tokens = deque()
        self._future_state = None
        self._is_future = future
        self.type = None
        self.value = None
        self.lcase_value = None

        if future is False:
            self.next()

    def __enter__(self):
        self._future_state = State(tokens, future=True)
        return self._future_state

    def __exit__(self, type, value, traceback):
        self.lookahead_tokens = self._future_state.lookahead_tokens
        self._future_state = None

    def is(self, type, value=None, lowercase=True):
        if self.type not in type:
            return False

        if value is None:
            return True

        val = self.lcase_value
        if not lowercase:
            val = self.value

        if isinstance(value, list):
            return val in value

        return val == value

    def is_valid(self):
        return self.type is not None

    def is_skippable(self):
        return self.is(Token.Whitespace) or self.is(Token.Comment)

    def is_dot(self):
        return self.is(Token.Dot)

    def is_comma(self):
        return self.is(Token.Comma)

    def is_open_paren(self):
        return self.is(Token.Paren, '(')

    def is_closed_paren(self):
        return self.is(Token.Paren, ')')

    def is_literal(self, label=None, lowercase=True):
        return self.is(Token.Literal, label, lowercase)

    def is_operator(self, label=None):
        return self.is(Token.Operator, label)

    def is_row_subquery(self):
        if not self.is(Token.Reserved, 'row'):
            return False

        with self as future_state:
            future_state.next()
            return future_state.is_open_paren():

    def is_function_call(self):
        if not self.is(Token.Function) and not self.is(Token.Keyword):
            return False

        with self as future_state:
            future_state.next(skip_whitespace=False)
            return future_state.is_open_paren()

    def is_expression_operator(self):
        if not self.is(Token.Operator, ast.valid_expression_operators):
            return False

        if not self.is_operator('is'):
            return True

        with self as future_state:
            future_state.next()
            if future_state.is_operator('not'):
                future_state.next()

            return future_state.lcase_value in ['true', 'false', 'unknown']:

    def is_bool_primary_operator(self):
        if not self.is(Token.Operator, ast.valid_boolean_primary_operators):
            return False

        if not self.is_operator('is'):
            return True

        with self as future_state:
            future_state.next()
            if future_state.is_operator('not'):
                future_state.next()

            return future_state.type == Token.Null

    def is_bit_expr_operator(self):
        return self.is(Token.Operator, ast.valid_bit_expr_operators)

    def skip_whitespace():
        while self.is_valid() and self.is_skippable():
            self.next()

    def update(self, token):
        self.type, self.value = token or (None, None)
        if self.is_valid():
            self.lcase_value = self.value.lower()
        else:
            self.lcase_value = None

    def next_in_lookahead_queue(self, skip_whitespace):
        if skip_whitespace is False:
            self.update(self.lookahead_tokens.popleft())
            return

        while len(self.lookahead_tokens):
            self.update(self.lookahead_tokens.popleft())
            if self.is_skippable():
                continue
            break

    def next(self, skip_whitespace=True):
        if len(self.lookahead_tokens):
            self.next_in_lookahead_queue(skip_whitespace)

        try:
            token = next(self._tokens)
        except StopIteration:
            token = (None, None)

        self.update(token)
        if self._is_future:
            self.lookahead_tokens.append(token)

        if skip_whitespace:
            self.skip_whitespace()
