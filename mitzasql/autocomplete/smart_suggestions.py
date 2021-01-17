import bisect
from mitzasql.utils import dfs, walk_ast
from mitzasql.db.model import *
import mitzasql.sql_parser.ast as Ast
import mitzasql.sql_parser.tokens as Token
import pudb

model = None
ast = None
last_node = None
prefix = None
suggestions_pool = {}

def set_smart_suggestions_model(sql_model):
    global model
    model = sql_model

def reset_suggestions_pool():
    global suggestions_pool
    suggestions_pool = {
            'columns': [],
            'tables': [],
            'aliases': []
    }

def add_to_pool(key, value):
    global suggestions_pool
    if value is None:
        return

    if isinstance(value, str):
        value = value.lower()
        if value == prefix:
            return

    if value in suggestions_pool[key]:
        return

    bisect.insort(suggestions_pool[key], value)

def filter_aliases(data, no_aliases=False):
    if not no_aliases or not len(suggestions_pool['aliases']):
        return data

    filtered_data = []
    for item in data:
        found_alias = False
        for alias in suggestions_pool['aliases']:
            if item in alias:
                found_alias = True
                break

        if not found_alias:
            filtered_data.append(item)

    return filtered_data

def create_suggestions_from_ast():
    global suggestions_pool
    reset_suggestions_pool()

    def node_inspector(node):
        if node.type == 'column' or node.type == 'table_reference':
            if not node.has_children():
                return

            pool_key = 'columns' if node.type == 'column' else 'tables'

            first_child = node.children[0]

            if first_child.type == 'identifier' and first_child.has_children():
                add_to_pool('tables', first_child.value)
                add_to_pool('columns', first_child.children[0].value)
            else:
                add_to_pool(pool_key, first_child.value)

            alias = node.get_child('alias')
            if alias is None or not alias.has_children():
                return
            add_to_pool(pool_key, alias.children[0].value)
            alias_value = alias.children[0].value
            suggestions_pool['aliases'].append({alias_value.lower(): first_child.value.lower()})
            return

    walk_ast(ast, node_inspector)

def detect_select_context(ast_node, is_child=True):
    if ast_node is None:
        return

    node_type = ast_node.type
    node_value = ast_node.value or ''
    node_value = node_value.lower()

    if node_type == 'column' or node_type == 'columns':
        return 'column'

    if node_type == 'index_hint':
        return node_type

    if node_type == 'table_reference' or node_type == 'from':
        return 'table'

    if node_type == 'where' or node_type == 'having' or node_type == 'order':
        return node_type

    if node_type == 'modifier':
        return 'select_modifier'

    if node_type == 'charset':
        return 'charset'

    if node_type == 'variable':
        return 'variable'

    return detect_select_context(ast_node.parent, is_child=False)

def table_name_from_alias(alias):
    for item in suggestions_pool['aliases']:
        if alias in item:
            return item[alias]

    return alias

def current_table_columns_suggestions():
    cols = model.columns
    for col in cols:
        add_to_pool('columns', col['name'])

    return suggestions_pool['columns']

def table_columns_suggestions(table_name):
    query = '''
        SELECT
            column_name
        FROM `information_schema`.`columns`
        WHERE
            table_schema = %(db_name)s
            AND
            table_name = %(table_name)s
        ORDER BY column_name
    '''

    try:
        cursor = model.connection.query(query, {
            'db_name': model.database,
            'table_name': table_name
            })
    except:
        return []

    data = cursor.fetchall()
    suggestions = []
    for row in data:
        add_to_pool('columns', row[0])

    return suggestions_pool['columns']


def column_suggestions(no_aliases=False):
    table_name = None
    if last_node.parent and last_node.parent.type == 'identifier':
        table_name = table_name_from_alias(last_node.parent.value)
        return filter_aliases(table_columns_suggestions(table_name), no_aliases)

    if table_name is None:
        if isinstance(model, TableModel):
            return filter_aliases(current_table_columns_suggestions(), no_aliases)

    return table_suggestions()

def order_suggestions():
    suggestions = column_suggestions()
    suggestions += ['asc', 'desc']
    return suggestions

def table_suggestions():
    query = '''
        SELECT
            TABLE_NAME AS Name
        FROM
            `information_schema`.`tables`
        WHERE TABLE_SCHEMA = %(db_name)s
        ORDER BY Name
        '''
    try:
        cursor = model.connection.query(query, {
            'db_name': model.database
            })
    except Exception as e:
        return []

    data = cursor.fetchall()
    for row in data:
        add_to_pool('tables', row[0])

    return suggestions_pool['tables']

def select_suggestions():
    if last_node is None:
        return []

    create_suggestions_from_ast()
    suggestions_context = detect_select_context(last_node)

    # print('aaaa')
    # print(suggestions_context)

    if suggestions_context is None:
        return []

    if suggestions_context == 'column' or suggestions_context == 'having':
        return column_suggestions()

    if suggestions_context == 'order':
        return order_suggestions()

    if suggestions_context == 'table':
        return table_suggestions()

    if suggestions_context == 'where':
        return column_suggestions(no_aliases=True)

    return []

def smart_suggestions(ast_, last_node_, prefix_):
    global ast
    global last_node
    global prefix
    ast = ast_
    last_node = last_node_
    prefix = prefix_

    # dfs(ast)

    suggestions = []
    if isinstance(ast, (Ast.Op, Ast.Expression)):
        return []

    if isinstance(ast, Ast.Statement):
        if ast.type == 'select':
            return select_suggestions()
