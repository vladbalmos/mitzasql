# Copyright (c) 2020 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
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

import bisect
import itertools
from pygments.lexers import _mysql_builtins
from mitzasql.sql_parser.parser import *
from mitzasql.autocomplete.smart_suggestions import *
import pudb

word_separators = [' ', '\t', '\n', '.', ';', ',', '"', "'", '`', '#', '(',
                   ')', '[', ']', '/', '=', '<', '>', '\\', '|', '+', '-', '%', '*']

mysql_keywords = itertools.chain(_mysql_builtins.MYSQL_DATATYPES,
        _mysql_builtins.MYSQL_FUNCTIONS, _mysql_builtins.MYSQL_OPTIMIZER_HINTS,
        _mysql_builtins.MYSQL_KEYWORDS)

keywords_pool = {}
for kw in mysql_keywords:
    c = kw[0]
    if c not in keywords_pool:
        keywords_pool[c] = []

    bisect.insort(keywords_pool[c], kw.lower())


class SQLAutocompleteEngine:
    def __init__(self, model):
        set_smart_suggestions_model(model)
        self._last_search = None
        self._cached_suggestions = []
        self._cached_prefix = None


    def _get_keyword_prefix(self, text):
        pos = len(text)
        prefix = ''
        while (True):
            if pos == 0:
                break

            char = text[pos - 1]
            if char in word_separators:
                break

            prefix = f'{char}{prefix}'
            pos -= 1

        return prefix

    def get_suggestions(self, text, pos):
        text = text[0:pos]
        if self._last_search == text and self._cached_suggestions is not None:
            return self._cached_suggestions, self._cached_prefix

        self._last_search = text
        prefix = self._get_keyword_prefix(text)

        suggestions = []
        ast = parse(text)

        if not len(ast):
            suggestions = self._dumb_suggestions(prefix)
        else:
            ast = ast[0]
            last_node = get_last_parsed_node()
            suggestions = smart_suggestions(ast, last_node)

        suggestions += self._dumb_suggestions(prefix)

        self._cached_suggestions = list(filter(lambda str: str.startswith(prefix.lower()), suggestions))
        self._cached_prefix = prefix
        return self._cached_suggestions, self._cached_prefix

    def get_word_separators(self):
        return word_separators

    def _dumb_suggestions(self, prefix):
        if not prefix:
            return []

        first_char = prefix[0].lower()

        try:
            suggestions = keywords_pool[first_char]
            return suggestions
        except:
            return []
