# TODO: fix querying hex numbers
import string

class Parser():

    def __init__(self, sql):
        self._raw_str = sql
        self._pos = 0
        self._tokens = []

    def _create_token(self, token, value):
        print(token + ' ' + value)
        self._tokens.append((token, value))

    def _parse_unquoted_identifier(self):
        word = ''
        while True:
            try:
                char = self._raw_str[self._pos]
            except IndexError:
                return word

            if char.isalnum() or char == '_' or char == '$':
                word += char
                self._pos += 1
                continue

            break

        return word

    def _parse_dec_number(self):
        number = ''
        while True:
            try:
                char = self._raw_str[self._pos]
            except IndexError:
                return number

            if char == '.' or char.isdigit():
                number += char
                self._pos += 1
                continue

            if char.lower() == 'e':
                # TODO handle column names which look like 11e
                if not len(number):
                    break

                if not number[len(number) - 1].isdigit():
                    break

                next_char = self._next_char()
                if not next_char or not next_char.isdigit():
                    break

                number += char
                self._pos += 1
                continue

            break
        return number

    def _parse_hex_number(self):
        number = ''
        while True:
            try:
                char = self._raw_str[self._pos]
            except IndexError:
                return number

            if char.lower() == 'x' or char == "'" or char in string.hexdigits:
                number += char
                self._pos += 1
                continue
            break

        return number

    def _parse_string(self):
        string_ = u''
        match_quote = None

        while True:
            try:
                char = self._raw_str[self._pos]
            except IndexError:
                return string_

            if (char == u'"' or char == u"'") and not match_quote:
                match_quote = char
                self._pos += 1
                continue

            if char == u'\\' and self._next_char() == match_quote:
                string_ += char + self._next_char()
                self._pos += 2
                continue

            if char == match_quote:
                self._pos += 1
                break

            string_ += char
            self._pos += 1

        return string_

    def _parse_quoted_identifier(self):
        string_ = u''
        match_quote = None

        while True:
            try:
                char = self._raw_str[self._pos]
            except IndexError:
                return string_

            if char == u'`' and not match_quote:
                match_quote = char
                self._pos += 1
                continue

            if char == match_quote:
                self._pos += 1
                break

            string_ += char
            self._pos += 1

        return string_

    def _parse_operator(self):
        operator = u''
        while True:
            try:
                char = self._raw_str[self._pos]
            except IndexError:
                return operator

            if char not in u'&>=<!%*+-/:^|~':
                break

            operator += char
            self._pos += 1
        return operator


    def _next_char(self, increment = 1):
        try:
            return self._raw_str[self._pos + increment]
        except IndexError:
            return None

    def parse(self):
        if not len(self._raw_str):
            return self._tokens

        while True:
            try:
                char = self._raw_str[self._pos]
            except IndexError:
                return self._tokens

            ##########
            # Literals
            ##########

            # parse white space
            if char.isspace():
                self._create_token('space', char)
                self._pos += 1
                continue

            if char == ',':
                self._create_token('separator', char)
                self._pos += 1
                continue

            if char == '(' or char == ')':
                self._create_token('paren', char)
                self._pos += 1
                continue

            # parse dec and hex (0x1AF) numbers
            if char.isdigit():
                if char == '0' and self._next_char() == 'x' and self._next_char(2) in string.digits:
                    number = self._parse_hex_number()
                else:
                    number = self._parse_dec_number()
                self._create_token('number', number)
                continue

            # parse hexadecimal X'01af' numbers
            if char.lower() == 'x' and self._next_char() == "'" and self._next_char(2) in string.hexdigits:
                number = self._parse_hex_number()
                self._create_token('number', number)
                continue

            # parse floating numbers starting with dot (.)
            if char == '.':
                if self._next_char() in string.digits:
                    number = self._parse_dec_number()
                    self._create_token('number', number)
                    continue

                # parse schema separator (.)
                self._create_token('dot', char)
                self._pos += 1
                continue

            # parse operators
            if char in u'&>=<!%*+-/:^|~':
                # TODO: operators
                operator = self._parse_operator()
                self._create_token('operator', operator)
                continue

            # parse strings
            if char == '"' or char == "'":
                string_ = self._parse_string()
                self._create_token('string', string_)
                continue

            # parse unquoted identifier
            if char.isalnum() or char == '_' or char == '$':
                identifier = self._parse_unquoted_identifier()
                self._create_token('unquoted_identifier', identifier)
                continue

            # parse quoted identifier
            if char == u'`':
                identifier = self._parse_quoted_identifier()
                self._create_token('quoted_identifier', identifier)
                continue

            # parse variables
            if char == u'@':
                var = self._parse_variable()
                self._create_token('variable', var)

            # TODO: comments













