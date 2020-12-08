import string

symbol_operators = [
    '->>',
    '<=>',
    '>>',
    '>=',
    '<>',
    '!=',
    '<<',
    '<=',
    '->',
    ':=',
    '&',
    '>',
    '<',
    '%',
    '*',
    '+',
    '-',
    '-',
    '/',
    '=',
    '=',
    '^'
]

class Parser():

    def __init__(self, sql):
        self.raw_str = sql
        self.pos = 0
        self.tokens = []

    def create_token(self, token, value):
        print(token + ' ' + value)
        self.tokens.append((token, value))

    def parse_unquoted_identifier(self):
        word = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                return word

            if char.isalnum() or char == '_' or char == '$':
                word += char
                self.pos += 1
                continue

            break

        return word

    def parse_dec_number(self):
        '''
        Returns False if scientific notation is invalid (missing exponent: 10e)
        '''
        number = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                return number

            if char == '.' or char.isdigit():
                number += char
                self.pos += 1
                continue

            if number[len(number) - 1].lower() == 'e' and char == '-':
                number += char
                self.pos += 1
                continue

            if char.lower() == 'e':
                if not len(number):
                    break

                if not number[len(number) - 1].isdigit():
                    break

                next_char = self._next_char()
                if not next_char or (next_char.isdigit() is False and next_char != '-'):
                    decrement_pos = len(number)
                    if number[0] == '.':
                        decrement_pos -= 1
                        self.create_token('dot', number[0])
                    self.pos -= decrement_pos
                    identifier = self.parse_unquoted_identifier()
                    self.create_token('unquoted_identifier', identifier)
                    return False

                number += char
                self.pos += 1
                continue

            break
        return number

    def parse_hex_number(self):
        number = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                return number

            if not len(number):
                if char == '0' or char.lower() == 'x':
                    number += char
                    self.pos += 1
                    continue
                break

            if len(number) == 1:
                if number[0] == '0':
                    if char == 'x':
                        number += char
                        self.pos += 1
                        continue
                    break

                if number[0].lower() == 'x':
                    if char == "'":
                        number += char
                        self.pos += 1
                        continue
                    break

                break

            if number[0] == '0':
                if char in string.hexdigits:
                    number += char
                    self.pos += 1
                    continue
                break

            if char in string.hexdigits or char == "'":
                number += char
                self.pos += 1
                continue

            break
        return number

    def parse_string(self):
        string_ = ''
        match_quote = None

        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                return string_

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
                string_ += char
                self.pos += 1
                break

            string_ += char
            self.pos += 1

        return string_

    def parse_quoted_identifier(self):
        string_ = ''
        match_quote = None

        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                return string_

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

        return string_

    def parse_operator(self, base = ''):
        operator = base
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                return operator

            if char not in '&>=<!%*+-/:^|~':
                break

            operator += char
            self.pos += 1

            if len(operator) < 3 and operator in symbol_operators:
                operator = self.parse_operator(operator)

            if len(operator) > 1:
                if operator in symbol_operators:
                    return operator
                self.pos -= 1
                return operator[0:len(operator) - 1]

        return operator

    def parse_variable(self):
        var = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                return operator

            if char == '@' and not len(var):
                var += char
                self.pos += 1
                continue
            elif char == '@' and len(var):
                break

            if char == '"' or char == "'":
                var += self.parse_string()
                continue

            if char == '`':
                var += self.parse_quoted_identifier()
                continue

            var += self.parse_unquoted_identifier()
            break

        return var


    def _next_char(self, increment = 1):
        try:
            return self.raw_str[self.pos + increment]
        except IndexError:
            return None

    def parse(self):
        if not len(self.raw_str):
            return self.tokens

        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                return self.tokens

            ##########
            # Literals
            ##########

            # parse white space
            if char.isspace():
                self.create_token('space', char)
                self.pos += 1
                continue

            if char == ',':
                self.create_token('separator', char)
                self.pos += 1
                continue

            if char == '(' or char == ')':
                self.create_token('paren', char)
                self.pos += 1
                continue

            # parse dec and hex (0x1AF) numbers
            if char.isdigit():
                if char == '0' and self._next_char() == 'x' and self._next_char(2) in string.hexdigits:
                    number = self.parse_hex_number()
                else:
                    number = self.parse_dec_number()
                    if number is False:
                        continue
                self.create_token('number', number)
                continue

            # parse hexadecimal X'01af' numbers
            if char.lower() == 'x' and self._next_char() == "'" and self._next_char(2) in string.hexdigits:
                number = self.parse_hex_number()
                self.create_token('number', number)
                continue

            # parse floating numbers starting with dot (.)
            if char == '.':
                if self._next_char() in string.digits:
                    number = self.parse_dec_number()
                    if number is False:
                        continue
                    self.create_token('number', number)
                    continue

                # parse schema separator (.)
                self.create_token('dot', char)
                self.pos += 1
                continue

            # parse operators
            if char in '&>=<!%*+-/:^|~':
                operator = self.parse_operator()
                self.create_token('operator', operator)
                continue

            # parse strings
            if char == '"' or char == "'":
                string_ = self.parse_string()
                self.create_token('string', string_)
                continue

            # parse unquoted identifier
            if char.isalnum() or char == '_' or char == '$':
                identifier = self.parse_unquoted_identifier()
                self.create_token('unquoted_identifier', identifier)
                continue

            # parse quoted identifier
            if char == '`':
                identifier = self.parse_quoted_identifier()
                self.create_token('quoted_identifier', identifier)
                continue

            # parse variables
            if char == '@':
                var = self.parse_variable()
                self.create_token('variable', var)

            # TODO: bit
            # TODO: comments













