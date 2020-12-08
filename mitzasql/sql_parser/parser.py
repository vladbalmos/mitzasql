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

    def create_token(self, token):
        if token is False:
            return
        print(token)
        self.tokens.append(token)

    def combine(self, *parsers):
        def parser():
            for parser in parsers:
                result = parser()
                if result is not False:
                    return result
            return False

        return parser

    def parse_dot(self):
        try:
            char = self.raw_str[self.pos]
        except IndexError:
            return False

        if char == '.':
            self.pos += 1
            return ('dot', char)

        self.pos -= 1
        return False

    def parse_paren(self):
        try:
            char = self.raw_str[self.pos]
        except IndexError:
            return False

        if char == '(' or char == ')':
            self.pos += 1
            return ('paren', char)

        self.pos -= 1
        return False

    def parse_separator(self):
        try:
            char = self.raw_str[self.pos]
        except IndexError:
            return False

        if char == ',':
            self.pos += 1
            return ('separator', char)

        self.pos -= 1
        return False

    def parse_space(self):
        space = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                return ('space', space)

            if char.isspace():
                space += char
                self.pos += 1
                continue

            break

        return ('space', space)

    def parse_unquoted_identifier(self):
        identifier = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                return ('unquoted_identifier', identifier)

            if char.isalnum() or char == '_' or char == '$':
                identifier += char
                self.pos += 1
                continue

            break

        return ('unquoted_identifier', identifier)

    def parse_dec_number(self):
        '''
        Returns False if scientific notation is invalid (missing exponent: 10e)
        '''
        number = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                return ('number', number)

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
                    self.pos -= decrement_pos
                    return False

                number += char
                self.pos += 1
                continue

            break
        return ('number', number)

    def parse_hex_number(self):
        number = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                return ('number', number)

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
        return ('number', number)

    def parse_string(self):
        string_ = ''
        match_quote = None

        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                return ('string', string_)

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

        return ('string', string_)

    def parse_quoted_identifier(self):
        string_ = ''
        match_quote = None

        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                return ('quoted_identifier', string_)

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

        return ('quoted_identifier', string_)

    def parse_operator(self, base = ''):
        operator = base
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                return ('operator', operator)

            if char not in '&>=<!%*+-/:^|~':
                break

            operator += char
            self.pos += 1

            if len(operator) < 3 and operator in symbol_operators:
                _, operator = self.parse_operator(operator)

            if len(operator) > 1:
                if operator in symbol_operators:
                    return ('operator', operator)
                self.pos -= 1
                return ('operator', operator[0:len(operator) - 1])

        return ('operator', operator)

    def parse_variable(self):
        var = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                return ('variable', var)

            if char == '@' and not len(var):
                var += char
                self.pos += 1
                continue
            elif char == '@' and len(var):
                break

            if char == '"' or char == "'":
                _, identifier = self.parse_string()
                var += identifier
                continue

            if char == '`':
                _, identifier = self.parse_quoted_identifier()
                var += identifier
                continue

            _, identifier = self.parse_unquoted_identifier()
            var += identifier
            break

        return ('variable', var)


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
                self.create_token(self.parse_space())
                continue

            if char == ',':
                self.create_token(self.parse_separator())
                continue

            if char == '(' or char == ')':
                self.create_token(self.parse_paren())
                continue

            # parse dec and hex (0x1AF) numbers
            if char.isdigit():
                # if char == '0' and self._next_char() == 'x' and self._next_char(2) in string.hexdigits:
                    # number = self.parse_hex_number()
                # else:
                    # number = self.parse_dec_number()
                    # if number is False:
                        # continue
                # self.create_token('number', number)
                # continue

                if char == '0' and self._next_char() == 'x' and self._next_char(2) in string.hexdigits:
                    parser = self.parse_hex_number
                else:
                    parser = self.parse_dec_number

                dot_identifier = self.combine(self.parse_dot, self.parse_unquoted_identifier)
                result = self.combine(parser, dot_identifier)()
                print('------------------')
                print(result)
                # self.create_token(identifier)
                continue

            # parse hexadecimal X'01af' numbers
            if char.lower() == 'x' and self._next_char() == "'" and self._next_char(2) in string.hexdigits:
                number = self.parse_hex_number()
                self.create_token(number)
                continue

            # parse floating numbers starting with dot (.)
            if char == '.':
                if self._next_char() in string.digits:
                    number = self.parse_dec_number()
                    if number is False:
                        continue
                    self.create_token(number)
                    continue

                # parse schema separator (.)
                self.create_token(self.parse_dot())
                continue

            # parse operators
            if char in '&>=<!%*+-/:^|~':
                operator = self.parse_operator()
                self.create_token(operator)
                continue

            # parse strings
            if char == '"' or char == "'":
                string_ = self.parse_string()
                self.create_token(string_)
                continue

            # parse unquoted identifier
            if char.isalnum() or char == '_' or char == '$':
                identifier = self.parse_unquoted_identifier()
                self.create_token(identifier)
                continue

            # parse quoted identifier
            if char == '`':
                identifier = self.parse_quoted_identifier()
                self.create_token(identifier)
                continue

            # parse variables
            if char == '@':
                var = self.parse_variable()
                self.create_token(var)

            # TODO: bit
            # TODO: comments













