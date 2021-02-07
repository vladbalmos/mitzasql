# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import bisect
import itertools
from pygments.lexers import _mysql_builtins
from ..sql_parser.parser import (parse, get_last_parsed_node)
from .smart_suggestions import (smart_suggestions, set_smart_suggestions_model)

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
    '''
    Uses the sql_parser module to generate ASTs from a SQL string
    and determine possible suggestions. If that fails, fall back to
    "dumb" suggestions (reserved keywords)
    '''
    def __init__(self, model):
        self._model = model
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
        set_smart_suggestions_model(self._model)
        text = text[0:pos]
        if self._last_search == text and self._cached_suggestions is not None:
            return self._cached_suggestions, self._cached_prefix

        self._last_search = text
        prefix = self._get_keyword_prefix(text)

        ast = parse(text)

        if len(ast):
            last_node = get_last_parsed_node()
            suggestion_candidates = smart_suggestions(ast, last_node, prefix)
        else:
            suggestion_candidates = []

        suggestions = self._compile(suggestion_candidates, prefix)

        self._cached_suggestions = suggestions
        self._cached_prefix = prefix
        return self._cached_suggestions, self._cached_prefix

    def get_word_separators(self):
        return word_separators

    def _compile(self, candidates, prefix):
        candidates += [self._dumb_suggestions(prefix)]

        compiled_suggestions = []
        for sugg_set in candidates:
            filtered_set = list(filter(lambda str: str.startswith(prefix.lower()), sugg_set))
            if not len(filtered_set):
                continue

            for item in filtered_set:
                if item not in compiled_suggestions:
                    compiled_suggestions.append(item)

        return compiled_suggestions

    def _dumb_suggestions(self, prefix):
        if not prefix:
            return []

        first_char = prefix[0].lower()

        try:
            suggestions = keywords_pool[first_char]
            return suggestions
        except:
            return []
