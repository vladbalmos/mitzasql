import bisect
import itertools
from pygments.lexers import _mysql_builtins
from mitzasql.utils import dfs
import mitzasql.sql_parser.ast as Ast
import mitzasql.sql_parser.tokens as Token
from mitzasql.autocomplete.context import detect_context
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

    def _get_child_at_pos(self, pos, node=None, last_pos=0, last_node=None):
        # pudb.set_trace()
        node = node or self._ast
        node_pos = node.pos or last_pos

        if node_pos == pos:
            return (node, node_pos)
        if node_pos > pos:
            return (last_node, last_pos)

        last_node = node
        last_pos = node_pos
        for child in node.children:
            child_node, child_pos = self._get_child_at_pos(pos, child, last_pos=last_pos, last_node=last_node)
            if child_pos == pos:
                return (child_node, child_pos)

            if child_pos > pos:
                return (last_node, last_pos)

            last_node = child_node
            last_pos = child_pos

        return (last_node, last_pos)

    def get(self):
        dfs(self._ast)
        node, pos = self._get_child_at_pos(self._pos)
        print('node found')
        dfs(node)
        if node is None:
            return []

        suggestions_context = detect_context(node)
        print('suggestion context is')
        print(suggestions_context)

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

