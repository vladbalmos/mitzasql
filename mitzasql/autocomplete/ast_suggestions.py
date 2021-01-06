import bisect
import itertools
from pygments.lexers import _mysql_builtins
from mitzasql.utils import dfs
import mitzasql.sql_parser.ast as Ast
import mitzasql.sql_parser.tokens as Token
import pudb

mysql_keywords = itertools.chain(_mysql_builtins.MYSQL_DATATYPES,
        _mysql_builtins.MYSQL_FUNCTIONS, _mysql_builtins.MYSQL_OPTIMIZER_HINTS,
        _mysql_builtins.MYSQL_KEYWORDS)

keywords_pool = {}
for kw in mysql_keywords:
    c = kw[0]
    if c not in keywords_pool:
        keywords_pool[c] = []

    bisect.insort(keywords_pool[c], kw.lower())

class SelectASTSuggestions:
    def __init__(self, connection, ast, prefix, pos):
        self._connection = connection
        self._ast = ast
        self._prefix = prefix
        self._pos = pos

    def _search_for_child(self, node=None):
        node = node or self._ast
        node_pos = node.pos or 0

        if self._pos > node_pos:
            for child in node.children:
                found_node = self._search_for_child(child)
                if found_node:
                    return found_node

        return node

    def _detect_suggestions_type(self, node):
        node_type = node.type
        node_value = node.value or ''
        node_value = node_value.lower()

        if node_type == 'alias' or node_type == 'literal':
            return self._detect_suggestions_type(node.parent)

        if node_type == 'column' or node_type == 'columns':
            return 'column'

        if node_type == 'index_hint':
            return node_type

        if node_type == 'table_reference' or node_type == 'from':
            return 'table'

        if node_type == 'where' or node_type == 'having':
            return node_type

        if node_type == 'modifier':
            return 'select_modifier'

        if node_type == 'charset':
            return 'charset'

        if node_type == 'variable':
            return 'variable'

    def get(self):
        node = self._search_for_child()
        if node is None:
            return []

        suggestions_type = self._detect_suggestions_type(node)

        return []

class ASTSuggestions:

    def __init__(self, connection):
        self._connection = connection

    def get(self, ast, prefix, pos):
        if not len(ast):
            return self._dumb_suggestions(prefix)

        ast = ast[0]
        if isinstance(ast, (Ast.Op, Ast.Expression)):
            return self._dumb_suggestions(prefix)

        if isinstance(ast, Ast.Statement):
            if ast.type == 'select':
                return self._select_suggestions(ast, prefix, pos)

        return self._dumb_suggestions(prefix)

    def _select_suggestions(self, ast, prefix, pos):
        select_ast_suggestions = SelectASTSuggestions(self._connection, ast, prefix, pos)
        suggestions = select_ast_suggestions.get()
        if not len(suggestions):
            suggestions = self._dumb_suggestions(prefix)
        return suggestions

    def _dumb_suggestions(self, prefix):
        if not prefix:
            return []

        first_char = prefix[0].lower()

        try:
            suggestions = keywords_pool[first_char]
            return suggestions
        except:
            return []

