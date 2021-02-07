# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

from collections import deque
from . import ast
from . import tokens as Token

class State:
    '''
    Models the current parser state.
    Also contains helper methods for lookahead and for determining
    current and future node types
    '''
    def __init__(self, tokens, future=False, prev_state_lookahead=None):
        self._tokens = tokens
        self.lookahead_tokens = deque()
        self.prev_state_lookahead = prev_state_lookahead
        self._future_state = None
        self._is_future = future
        self.type = None
        self.value = None
        self.lcase_value = None
        self.pos = None

        if not future:
            self.next()

    def __bool__(self):
        return self.type is not None

    def __enter__(self):
        self._future_state = State(self._tokens, future=True, prev_state_lookahead=self.lookahead_tokens.copy())
        return self._future_state

    def __exit__(self, type, value, traceback):
        if self._future_state is not None:
            self.lookahead_tokens.extend(self._future_state.lookahead_tokens)
        self._future_state = None

    def token_is(self, type, value=None, lowercase=True, equal_type=False):
        if equal_type:
            if self.type != type:
                return False
        else:
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

    def is_other(self, label=None, lowercase=True):
        return self.token_is(Token.Other, label, lowercase)

    def is_name(self, label=None, lowercase=True):
        return self.token_is(Token.Name, label, lowercase)

    def is_variable(self, label=None, lowercase=True):
        return self.token_is(Token.Variable, label, lowercase)

    def is_keyword(self, label=None, lowercase=True):
        return self.token_is(Token.Keyword, label, lowercase)

    def is_function(self, label=None, lowercase=True):
        return self.token_is(Token.Function, label, lowercase)

    def is_param_marker(self, label=None, lowercase=True):
        return self.token_is(Token.ParamMarker, label, lowercase)

    def is_reserved(self, label=None, lowercase=True):
        return self.token_is(Token.Reserved, label, lowercase, equal_type=True)

    def is_skippable(self):
        return self.token_is(Token.Whitespace) or self.token_is(Token.Comment)

    def is_dot(self):
        return self.token_is(Token.Dot)

    def is_comma(self):
        return self.token_is(Token.Comma)

    def is_semicolon(self):
        return self.token_is(Token.Semicolon)

    def is_open_paren(self):
        return self.token_is(Token.Paren, '(')

    def is_closed_paren(self):
        return self.token_is(Token.Paren, ')')

    def is_literal(self, label=None, lowercase=True):
        return self.token_is(Token.Literal, label, lowercase)

    def is_operator(self, label=None):
        return self.token_is(Token.Operator, label)

    def is_delimiter(self):
        return self.token_is(Token.Punctuation) or self.token_is(Token.Paren)

    def is_identifier(self):
        if not self:
            return False

        if self.is_name():
            return True

        if self.is_other() or self.is_keyword() or self.is_function():
            with self as future_state:
                future_state.next()
                return future_state.is_dot()

    def is_column_alias(self):
        if not self or self.is_delimiter():
            return False

        if self.is_reserved('as'):
            return True

        if self.is_literal() or self.is_name() or self.is_other():
            return True

        with self as future_state:
            future_state.next()
            return future_state.is_comma()

    def is_row_subquery(self):
        if not self:
            return False

        if not self.token_is(Token.Reserved, 'row'):
            return False

        with self as future_state:
            future_state.next()
            return future_state.is_open_paren()

    def is_subquery(self):
        if not self:
            return False

        if not self.is_open_paren():
            return False

        with self as future_state:
            future_state.next()
            return future_state.is_reserved('select')

    def is_function_call(self):
        if not self:
            return False

        if not self.token_is(Token.Function) and not self.is_keyword() and not self.is_other():
            return False

        with self as future_state:
            future_state.next(skip_whitespace=False)
            return future_state.is_open_paren()

    def is_expression_operator(self):
        if not self:
            return False

        if not self.token_is(Token.Operator, ast.valid_expression_operators):
            return False

        if not self.is_operator('is'):
            return True

        with self as future_state:
            future_state.next()
            if future_state.is_operator('not'):
                future_state.next()

            return future_state.lcase_value in ['true', 'false', 'unknown']

    def is_bool_primary_operator(self):
        if not self:
            return False

        if not self.token_is(Token.Operator, ast.valid_boolean_primary_operators):
            return False

        if not self.is_operator('is'):
            return True

        with self as future_state:
            future_state.next()
            if future_state.is_operator('not'):
                future_state.next()

            return future_state.type == Token.Null

    def is_predicate_operator(self):
        if not self:
            return False

        if self.is_reserved('in'):
            return True

        if not self.is_operator('not') and not self.token_is(Token.Operator, ast.valid_predicate_operators):
            return False

        if not self.is_operator('not') and self.token_is(Token.Operator, ast.valid_predicate_operators):
            return True

        with self as future_state:
            future_state.next()
            return future_state.token_is(Token.Operator, ast.valid_predicate_operators) or future_state.is_reserved('in')

    def is_bit_expr_operator(self):
        return self.token_is(Token.Operator, ast.valid_bit_expr_operators)

    def skip_whitespace(self):
        while self and self.is_skippable():
            self.next()

    def update(self, token):
        self.type, self.value, self.pos = token or (None, None, None)
        if self:
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
                if not len(self.lookahead_tokens):
                    return self.next(skip_whitespace)
                continue
            break

    def next(self, skip_whitespace=True):
        if self._is_future and self.prev_state_lookahead and len(self.prev_state_lookahead):
            if skip_whitespace is False:
                self.update(self.prev_state_lookahead.popleft())
                return

            while len(self.prev_state_lookahead):
                self.update(self.prev_state_lookahead.popleft())
                if self.is_skippable():
                    continue
                break
            return

        if len(self.lookahead_tokens) and not self._is_future:
            self.next_in_lookahead_queue(skip_whitespace)
            return

        try:
            token = next(self._tokens)
        except StopIteration:
            token = (None, None, None)

        self.update(token)
        if self._is_future:
            self.lookahead_tokens.append(token)

        if skip_whitespace:
            self.skip_whitespace()
