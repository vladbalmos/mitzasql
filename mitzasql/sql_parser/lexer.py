# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import string
from . import tokens as Token
from . import keywords

class Lexer():
    '''
    SQL String tokenizer.
    Parses a string one char at a time
    '''

    def __init__(self, sql):
        self.raw_str = sql
        self.pos = 0
        self.tokens = []

    def _next_char(self, increment = 1):
        try:
            return self.raw_str[self.pos + increment]
        except IndexError:
            return None

    def _make_token(self, ttype, val):
        return (ttype, val, self.pos - len(val))

    def _looks_like_keyword(self, char):
        return char.isalnum() or char == '_' or char == '$'

    def either(self, *parsers):
        def either_parser():
            for parser in parsers:
                result = parser()
                if result is not False:
                    return result
            return False

        return either_parser

    def parse_dot(self):
        try:
            char = self.raw_str[self.pos]
        except IndexError:
            return False

        if char == '.':
            self.pos += 1
            return self._make_token(Token.Dot, char)

        return False

    def parse_paren(self):
        try:
            char = self.raw_str[self.pos]
        except IndexError:
            return False

        if char == '(' or char == ')':
            self.pos += 1
            return self._make_token(Token.Paren, char)

        return False

    def parse_semicolon(self):
        try:
            char = self.raw_str[self.pos]
        except IndexError:
            return False

        if char == ';':
            self.pos += 1
            return self._make_token(Token.Semicolon, char)

        return False

    def parse_comma(self):
        try:
            char = self.raw_str[self.pos]
        except IndexError:
            return False

        if char == ',':
            self.pos += 1
            return self._make_token(Token.Comma, char)

        return False

    def parse_whitespace(self):
        space = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                break

            if char.isspace():
                space += char
                self.pos += 1
                continue

            break

        if not len(space):
            return False

        return self._make_token(Token.Whitespace, space)

    def parse_unquoted_identifier(self):
        identifier = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                break

            if self._looks_like_keyword(char):
                identifier += char
                self.pos += 1
                continue

            break

        if not len(identifier):
            return False

        token = keywords.classify(identifier)

        return self._make_token(token, identifier)

    def parse_dec_number(self):
        '''
        Returns False if scientific notation is invalid (missing exponent: 10e)
        '''
        number = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                break

            if char == '.' or char.isdigit():
                number += char
                self.pos += 1
                continue

            if number[-1].lower() == 'e' and char == '-':
                number += char
                self.pos += 1
                continue

            if char.lower() == 'e':
                if not len(number):
                    break

                if 'e' in number:
                    break

                if not number[-1].isdigit():
                    break

                next_char = self._next_char()
                if not next_char or (next_char.isdigit() is False and next_char != '-'):
                    decrement_pos = len(number)
                    if number[0] == '.':
                        decrement_pos -= 1
                    self.pos -= decrement_pos
                    return False

                number += char
                self.pos += 1
                continue

            if self._looks_like_keyword(char):
                self.pos -= len(number)
                return False

            break

        if not len(number):
            return False

        if number[-1].lower() == 'e':
            self.pos -= len(number)
            return False

        if number == '.':
            self.pos -= 1
            return False

        return self._make_token(Token.Number.Dec, number)

    def parse_binary_number_ob(self):
        '''
        Parse binary numbers having the format 0b000
        '''
        number = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                break

            if not len(number):
                if char == '0':
                    number += char
                    self.pos += 1
                    continue
                break

            if len(number) == 1:
                if char == 'b':
                    number += char
                    self.pos += 1
                    continue
                break

            if char == '0' or char == '1':
                number += char
                self.pos += 1
                continue

            if self._looks_like_keyword(char):
                self.pos -= len(number)
                return False
            break


        if len(number) < 3:
            self.pos -= len(number)
            return False

        return self._make_token(Token.Number.Bit, number)

    def parse_hex_number_ox(self):
        '''
        Parse hex numbers having the format 0xfff
        '''
        number = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                break

            if not len(number):
                if char == '0':
                    number += char
                    self.pos += 1
                    continue
                break

            if len(number) == 1:
                if char == 'x':
                    number += char
                    self.pos += 1
                    continue
                break

            if char in string.hexdigits:
                number += char
                self.pos += 1
                continue

            if self._looks_like_keyword(char):
                self.pos -= len(number)
                return False

            break

        if len(number) < 3:
            self.pos -= len(number)
            return False

        return self._make_token(Token.Number.Hex, number)

    def parse_binary_number_b_quote(self):
        '''
        Parse binary number having the format b'010'
        '''
        number = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                break

            if not len(number):
                if char.lower() == 'b':
                    number += char
                    self.pos += 1
                    continue
                break

            if len(number) == 1:
                if char == "'":
                    number += char
                    self.pos += 1
                    continue
                break

            if char == '0' or char == '1':
                number += char
                self.pos += 1
                continue

            if char == "'":
                number += char
                self.pos += 1
                break

            if self._looks_like_keyword(char):
                self.pos -= len(number)
                return False

            break

        if len(number) < 3:
            self.pos -= len(number)
            return False

        if number[-1] != "'":
            self.pos -= len(number)
            return False

        if len(number) == 3 and number.lower() == "b''":
            self.pos -= len(number)
            return False

        return self._make_token(Token.Number.Bit, number)

    def parse_hex_number_x_quote(self):
        '''
        Parse hex number having the format x'fff'
        '''
        number = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                break

            if not len(number):
                if char.lower() == 'x':
                    number += char
                    self.pos += 1
                    continue
                break

            if len(number) == 1:
                if char == "'":
                    number += char
                    self.pos += 1
                    continue
                break

            if char in string.hexdigits:
                number += char
                self.pos += 1
                continue

            if char == "'":
                number += char
                self.pos += 1
                break

            if self._looks_like_keyword(char):
                self.pos -= len(number)
                return False

            break

        if len(number) < 3:
            self.pos -= len(number)
            return False

        if number[-1] != "'":
            self.pos -= len(number)
            return False

        if len(number) == 3 and number.lower() == "x''":
            self.pos -= len(number)
            return False

        return self._make_token(Token.Number.Hex, number)

    def parse_string(self):
        string_ = ''
        match_quote = None

        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                break

            if (char == '"' or char == "'") and not match_quote:
                match_quote = char
                string_ += char
                self.pos += 1
                continue

            if char == '\\' and self._next_char() == match_quote:
                string_ += char + self._next_char()
                self.pos += 2
                continue

            if char == match_quote:
                if self._next_char() == match_quote:
                    # Quote is escaped
                    string_ += char
                    self.pos += 2
                    continue
                string_ += char
                self.pos += 1
                break

            string_ += char
            self.pos += 1

        if not len(string_):
            return False

        return self._make_token(Token.String, string_)

    def parse_quoted_identifier(self):
        string_ = ''
        match_quote = None

        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                break

            if char == '`' and not match_quote:
                match_quote = char
                string_ += char
                self.pos += 1
                continue

            if char == match_quote:
                string_ += char
                self.pos += 1
                break

            string_ += char
            self.pos += 1

        if not len(string_):
            return False

        return self._make_token(Token.Name, string_)

    def parse_operator(self, base = ''):
        operator = base
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                break

            if char not in '&>=<!%*+-/:^|~':
                break

            operator += char
            self.pos += 1

            if len(operator) < 3 and operator in keywords.symbol_operators:
                result = self.parse_operator(operator)
                if not result:
                    return False
                _, operator, pos = result

            if len(operator) > 1:
                if operator in keywords.symbol_operators:
                    return self._make_token(Token.Operator.Symbol, operator)
                self.pos -= 1
                return self._make_token(Token.Operator.Symbol, operator[0:-1])

        if not len(operator):
            return False

        return self._make_token(Token.Operator.Symbol, operator)

    def parse_variable(self):
        var = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                break

            if char == '@' and not len(var):
                var += char
                self.pos += 1
                continue
            if char == '@' and len(var) == 1 and var[0] == '@':
                var += char
                self.pos += 1
                continue

            if char == '@' and len(var) > 1:
                break

            if char == '"' or char == "'":
                result = self.parse_string()
                if not result:
                    break

                var += result[1]
                break

            if char == '`':
                result = self.parse_quoted_identifier()
                if not result:
                    break

                var += result[1]
                break

            result = self.parse_unquoted_identifier()
            if not result:
                break

            var += result[1]

            if self._next_char(increment=0) == '.':
                var += '.'
                self.pos += 1
                continue
            break

        if not len(var):
            return False

        return self._make_token(Token.Variable, var)

    def parse_c_style_comment(self):
        comment = ''

        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                break

            if not len(comment):
                if char == '/':
                    comment += char
                    self.pos += 1
                    continue
                break

            if len(comment) == 1:
                if char == '*':
                    comment += char
                    self.pos += 1
                    continue
                break

            if char == '/' and comment[-1] == '*':
                comment += char
                self.pos += 1
                break

            comment += char
            self.pos += 1


        if len(comment) < 2:
            self.pos -= len(comment)
            return False

        return self._make_token(Token.Comment, comment)

    def parse_dash_style_comment(self):
        comment = ''

        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                break

            if not len(comment):
                if char == '-':
                    comment += char
                    self.pos += 1
                    continue
                break

            if len(comment) == 1:
                if char == '-':
                    comment += char
                    self.pos += 1
                    continue
                break

            if len(comment) == 2 and not char.isspace():
                break

            if char == '\n':
                comment += char
                self.pos += 1
                break

            comment += char
            self.pos += 1

        if len(comment) < 3:
            self.pos -= len(comment)
            return False

        return self._make_token(Token.Comment, comment)

    def parse_hash_style_comment(self):
        comment = ''

        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                break

            if not len(comment):
                if char == '#':
                    comment += char
                    self.pos += 1
                    continue
                break

            if char == '\n':
                comment += char
                self.pos += 1
                break

            comment += char
            self.pos += 1

        if not len(comment):
            return False

        return self._make_token(Token.Comment, comment)


    def tokenize(self):
        if not len(self.raw_str):
            return

        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                # return self.tokens
                return

            ##########
            # Literals
            ##########

            # parse white space
            if char.isspace():
                result = self.parse_whitespace()
                if result:
                    yield result
                    continue

            if char == ',':
                result = self.parse_comma()
                if result:
                    yield result
                    continue

            if char == '(' or char == ')':
                result = self.parse_paren()
                if result:
                    yield result
                    continue

            if char == ';':
                result = self.parse_semicolon()
                if result:
                    yield result
                    continue

            # parse dec, binary (0b01) and hex (0x1AF) numbers
            if char.isdigit():
                if char == '0':
                    if self._next_char() == 'x':
                        parser = self.parse_hex_number_ox
                    elif self._next_char().lower() == 'b':
                        parser = self.parse_binary_number_ob
                    else:
                        parser = self.parse_dec_number
                else:
                    parser = self.parse_dec_number

                parser = self.either(parser,
                                     self.either(self.parse_dot, self.parse_unquoted_identifier))
                result = parser()
                if result:
                    yield result
                    continue

            # parse hexadecimal X'01af' numbers
            if char.lower() == 'x' and self._next_char() == "'":
                parser = self.either(self.parse_hex_number_x_quote, self.parse_unquoted_identifier)
                result = parser()
                if result:
                    yield result
                    continue

            # parse binary b'01' numbers
            if char.lower() == 'b' and self._next_char() == "'":
                parser = self.either(self.parse_binary_number_b_quote, self.parse_unquoted_identifier)
                result = parser()
                if result:
                    yield result
                    continue

            # parse floating numbers starting with dot (.) or a single dot
            if char == '.':
                parser = self.either(self.parse_dec_number, self.parse_dot)
                result = parser()
                if result:
                    yield result
                    continue

            # parse /* c style comments */
            if char == '/' and self._next_char() == '*':
                result = self.parse_c_style_comment()
                if result:
                    yield result
                    continue

            # parse -- comments
            if char == '-' and self._next_char() == '-':
                parser = self.either(self.parse_dash_style_comment, self.parse_operator)
                result = parser()
                if result:
                    yield result
                    continue

            # parse operators
            if char in '&>=<!%*+-/:^|~':
                result = self.parse_operator()
                if result:
                    yield result
                    continue

            # parse strings
            if char == '"' or char == "'":
                result = self.parse_string()
                if result:
                    yield result
                    continue

            # parse quoted identifier
            if char == '`':
                result = self.parse_quoted_identifier()
                if result:
                    yield result
                    continue

            # parse variables
            if char == '@':
                result = self.parse_variable()
                if result:
                    yield result
                    continue

            # parse #hash style comment
            if char == '#':
                result = self.parse_hash_style_comment()
                if result:
                    yield result
                    continue

            # parse unquoted identifier
            if self._looks_like_keyword(char):
                result = self.parse_unquoted_identifier()
                if result:
                    yield result
                    continue

            if char == '?':
                self.pos += 1
                yield self._make_token(Token.ParamMarker, char)

            # we shouldn't be here, the syntax is wrong so we skip this character
            self.pos += 1
