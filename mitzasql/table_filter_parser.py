# Copyright (c) 2019 <name of copyright holder>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from mitzasql.state_machine import StateMachine
from mitzasql.logger import logger

# initial state: parse_char
#   if char is ' or '
#       goto state 'is quote'
#   else if char is [space] or end of string
#       goto state 'end'
#   else
#       goto state parse_char

class StopParsing(Exception):
    pass

class Parser:
    def __init__(self, string):
        self.string = string;
        self._tokens = []
        self._token_index = 0
        self._index = 0
        self._quote_is_open = False
        self._fsm = StateMachine('table_filter_parser', disable_logging=True)
        self._init_fsm()
        self._fsm.set_initial_state('parse')

    def parse(self):
        try:
            self._fsm.run(self._index)
        except StopParsing:
            pass
        return self.tokens

    @property
    def tokens(self):
        return list(filter(lambda token: len(token) > 0, self._tokens))

    def handle_char(self, index):
        try:
            char = self.string[index]
        except IndexError as e:
            char = None

        if char is None:
            return self._fsm.change_state('stop')

        if char == u' ':
            return self._fsm.change_state('found_space')

        if char == u"'":
            return self._fsm.change_state('found_quote', "'")

        if char == u'"':
            return self._fsm.change_state('found_quote', '"')

        if char == u'\\':
            return self._fsm.change_state('found_backslash')

        self._append_char(char)
        self._index += 1
        return self._fsm.change_state('next_char', self._index)

    def handle_space(self):
        if not self._quote_is_open:
            self._tokens.append(u'')
            self._token_index += 1
        else:
            self._append_char(u' ')
        self._index += 1
        return self._fsm.change_state('next_char', self._index)

    def handle_quote(self, quote_char):
        if self._quote_is_open != False:
            if self._quote_is_open == quote_char:
                self._quote_is_open = False
            else:
                self._append_char(quote_char)
            self._index += 1
            return self._fsm.change_state('next_char', self._index)

        self._quote_is_open = quote_char
        self._index += 1
        return self._fsm.change_state('next_char', self._index)

    def handle_backslash(self):
        try:
            next_char = self.string[self._index + 1]
        except IndexError:
            self._append_char(u'\\')
            self._fsm.change_state('stop')

        if next_char == self._quote_is_open:
            self._append_char(next_char)
            self._index += 2
        else:
            self._append_char(u'\\')
            self._index += 1
        return self._fsm.change_state('next_char', self._index)

    def handle_stop(self):
        raise StopParsing()

    def _init_fsm(self):
        self._fsm.add_state('parse', self.handle_char, {
            'found_space': 'on_space',
            'found_quote': 'on_quote',
            'found_backslash': 'on_backslash',
            'next_char': 'parse',
            'stop': 'on_stop'
            })
        self._fsm.add_state('on_space', self.handle_space, {
            'next_char': 'parse',
            })
        self._fsm.add_state('on_quote', self.handle_quote, {
            'next_char': 'parse',
            })
        self._fsm.add_state('on_backslash', self.handle_backslash, {
            'next_char': 'parse',
            })
        self._fsm.add_state('on_stop', self.handle_stop)

    def _append_char(self, char):
        try:
            token = self._tokens[self._token_index]
        except IndexError as e:
            self._tokens.append(u'')

        self._tokens[self._token_index] += char
