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

    def _next_char(self, increment = 1):
        try:
            return self.raw_str[self.pos + increment]
        except IndexError:
            return None

    def classify_identifier(self, identifier):
        if identifier == 'false' or identifier == 'FALSE' or identifier == 'true' or identifier == 'TRUE':
            return 'boolean'

        if identifier.lower() == 'null':
            return 'null'

        return 'unquoted_identifier'

    def create_token(self, token):
        if token is False:
            return
        print(token)
        self.tokens.append(token)

    def either(self, *parsers):
        def combined_parser():
            for parser in parsers:
                result = parser()
                if result is not False:
                    return result
            return False

        return combined_parser

    def parse_dot(self):
        try:
            char = self.raw_str[self.pos]
        except IndexError:
            return False

        if char == '.':
            self.pos += 1
            return ('dot', char)

        return False

    def parse_paren(self):
        try:
            char = self.raw_str[self.pos]
        except IndexError:
            return False

        if char == '(' or char == ')':
            self.pos += 1
            return ('paren', char)

        return False

    def parse_separator(self):
        try:
            char = self.raw_str[self.pos]
        except IndexError:
            return False

        if char == ',':
            self.pos += 1
            return ('separator', char)

        return False

    def parse_space(self):
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

        return ('space', space)

    def parse_unquoted_identifier(self):
        identifier = ''
        while True:
            try:
                char = self.raw_str[self.pos]
            except IndexError:
                break

            if char.isalnum() or char == '_' or char == '$':
                identifier += char
                self.pos += 1
                continue

            break

        if not len(identifier):
            return False

        token = self.classify_identifier(identifier)

        return (token, identifier)

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

        if not len(number):
            return False

        if number[-1].lower() == 'e':
            self.pos -= len(number)
            return False

        return ('number', number)

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

            if char.isalnum():
                self.pos -= len(number)
                return False
            break


        if len(number) < 3:
            self.pos -= len(number)
            return False

        return ('number', number)

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

            if char.isalnum():
                self.pos -= len(number)
                return False

            break

        if len(number) < 3:
            self.pos -= len(number)
            return False

        return ('number', number)

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

            if char.isalnum():
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

        return ('number', number)

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

            if char.isalnum():
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

        return ('number', number)

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
                string_ += char
                self.pos += 1
                break

            string_ += char
            self.pos += 1

        if not len(string_):
            return False

        return ('string', string_)

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

        return ('quoted_identifier', string_)

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

            if len(operator) < 3 and operator in symbol_operators:
                result = self.parse_operator(operator)
                if not result:
                    return False
                _, operator = result

            if len(operator) > 1:
                if operator in symbol_operators:
                    return ('operator', operator)
                self.pos -= 1
                return ('operator', operator[0:len(operator) - 1])

        if not len(operator):
            return False

        return ('operator', operator)

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
            elif char == '@' and len(var):
                break

            if char == '"' or char == "'":
                result = self.parse_string()
                if not result:
                    self.pos -= len(var)
                    return False

                var += result[1]
                break

            if char == '`':
                result = self.parse_quoted_identifier()
                if not result:
                    self.pos -= len(var)
                    return False

                var += result[1]
                break

            result = self.parse_unquoted_identifier()
            if not result:
                self.pos -= len(var)
                return False

            var += result[1]
            break

        if not len(var):
            return False

        if len(var) < 2:
            self.pos -= len(var)
            return False

        return ('variable', var)

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

        return ('comment', comment)

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

        return ('comment', comment)

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

        return ('comment', comment)


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
                self.create_token(result)
                continue

            # parse hexadecimal X'01af' numbers
            if char.lower() == 'x' and self._next_char() == "'":
                parser = self.either(self.parse_hex_number_x_quote, self.parse_unquoted_identifier)
                result = parser()
                self.create_token(result)
                continue

            # parse binary b'01' numbers
            if char.lower() == 'b' and self._next_char() == "'":
                parser = self.either(self.parse_binary_number_b_quote, self.parse_unquoted_identifier)
                result = parser()
                self.create_token(result)
                continue

            # parse floating numbers starting with dot (.) or a single dot
            if char == '.':
                parser = self.either(self.parse_dec_number, self.parse_dot)
                result = parser()
                self.create_token(result)
                continue

            # parse /* c style comments */
            if char == '/' and self._next_char() == '*':
                comment = self.parse_c_style_comment()
                self.create_token(comment)
                continue

            # parse -- comments
            if char == '-' and self._next_char() == '-':
                parser = self.either(self.parse_dash_style_comment, self.parse_operator)
                result = parser()
                self.create_token(result)
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

            # parse quoted identifier
            if char == '`':
                identifier = self.parse_quoted_identifier()
                self.create_token(identifier)
                continue

            # parse variables
            if char == '@':
                var = self.parse_variable()
                self.create_token(var)

            # parse #hash style comment
            if char == '#':
                comment = self.parse_hash_style_comment()
                self.create_token(comment)
                continue

            # parse unquoted identifier
            if char.isalnum() or char == '_' or char == '$':
                identifier = self.parse_unquoted_identifier()
                self.create_token(identifier)
                continue

            # we shouldn't be here, the syntax is wrong so we skip this character
            self.pos += 1

            # TODO classify identifiers (boolean, null, functions, statements, operators)













