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
            'databases': [],
            'tables': [],
            'aliases': []
    }

def add_to_pool(key, value):
    global suggestions_pool
    if value is None:
        return

    value = value.lower().replace('`', '')
    if value == prefix:
        return

    if value in suggestions_pool[key]:
        return

    bisect.insort(suggestions_pool[key], value)

def filter_columns(data, no_aliases=False, filter_star_operator=False):
    if not no_aliases and not filter_star_operator:
        return data

    filtered_data = []
    for item in data:
        if filter_star_operator and item == '*':
            continue

        if no_aliases:
            found_alias = False
            for alias in suggestions_pool['aliases']:
                if item in alias:
                    found_alias = True
                    break

            if not found_alias:
                filtered_data.append(item)
        else:
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
            suggestions_pool['aliases'].append({alias_value.lower().replace('`', ''): first_child.value.lower().replace('`', '')})
            return

    walk_ast(ast, node_inspector)

def detect_select_next_possible_keywords(context):
    if context == 'column':
        return ['from']

    if context == 'table':
        return ['where', 'group', 'by', 'having', 'order', 'limit']

    if context == 'where':
        return ['group', 'by', 'having', 'order', 'limit']

    if context == 'group':
        return ['having', 'order', 'limit']

    if context == 'having':
        return ['order', 'limit']

    if context == 'order':
        return ['limit']

    return []

def detect_select_context(ast_node, is_child=True):
    if ast_node is None:
        return

    node_type = ast_node.type
    node_value = ast_node.value or ''
    node_value = node_value.lower()

    if node_type == 'column' or node_type == 'columns' or node_type == 'join_spec':
        return 'column'

    if node_type == 'index_hint':
        return node_type

    if node_type == 'table_reference' or node_type == 'from':
        return 'table'

    if node_type in ('where', 'having', 'order', 'group'):
        return node_type

    if node_type == 'modifier':
        return 'select_modifier'

    if node_type == 'charset':
        return 'charset'

    if node_type == 'variable':
        return 'variable'

    return detect_select_context(ast_node.parent, is_child=False)

def is_alias(alias):
    for item in suggestions_pool['aliases']:
        if alias in item:
            return True
    return False

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

def table_columns_suggestions(table_name, db_name=None, return_from_pool=True):
    if isinstance(table_name, str):
        table_name = [table_name.replace('`', '')]

    table_name = [item.lower().replace('`', '') for item in table_name]

    query = '''
        SELECT
            column_name
        FROM `information_schema`.`columns`
        WHERE
            LOWER(table_schema) = LOWER(%(db_name)s)
            AND
            LOWER(table_name) in ("{0}")
        ORDER BY column_name
    '''.format('","'.join(table_name))

    db_name = db_name if db_name is not None else model.database
    try:
        cursor = model.connection.query(query, {
            'db_name': db_name
            })
    except:
        return []

    data = cursor.fetchall()
    columns = [row[0] for row in data]
    for col in columns:
        add_to_pool('columns', col)

    if return_from_pool:
        return suggestions_pool['columns']

    return columns


def column_suggestions(context='column'):
    no_aliases = True if context == 'where' else False
    filter_star_operator = False

    if last_node.parent and last_node.parent.type == 'identifier':
        table_name = table_name_from_alias(last_node.parent.value.replace('`', ''))
        parent_node = last_node.parent.parent
        db_name = None
        if parent_node.type == 'identifier':
            db_name = parent_node.value.replace('`', '')

        return filter_columns(table_columns_suggestions(table_name, db_name=db_name, return_from_pool=False), no_aliases, filter_star_operator=True)

    table_names = []
    if context in ('where', 'group', 'having', 'order'):
        table_names = suggestions_pool['tables']
        filter_star_operator = True

    if not len(table_names):
        if isinstance(model, TableModel):
            return filter_columns(current_table_columns_suggestions(), no_aliases, filter_star_operator)
    else:
        return filter_columns(table_columns_suggestions(table_names), no_aliases, filter_star_operator)

    return []

def database_suggestions():
    query = 'SHOW DATABASES'
    try:
        cursor = model.connection.query(query)
    except Exception as e:
        return []

    data = cursor.fetchall()
    for row in data:
        add_to_pool('databases', row[0])

    return suggestions_pool['databases']

def table_suggestions(database=None, return_from_pool=True):
    if database is None:
        if last_node.parent and last_node.parent.type == 'identifier':
            return table_suggestions(last_node.parent.value.replace('`', ''), return_from_pool=False)
        else:
            database = model.database

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
            'db_name': database
            })
    except Exception as e:
        return []

    data = cursor.fetchall()
    tables = [row[0] for row in data]
    for table in tables:
        add_to_pool('tables', table)

    if return_from_pool:
        return suggestions_pool['tables']
    return tables

def select_suggestions():
    if last_node is None:
        return []

    create_suggestions_from_ast()
    suggestions_context = detect_select_context(last_node)

    if suggestions_context is None:
        return []

    if suggestions_context == 'table':
        return [table_suggestions(), database_suggestions(), detect_select_next_possible_keywords(suggestions_context)]

    if suggestions_context in ('column', 'where', 'group', 'having', 'order'):
        col_suggestions =  column_suggestions(context=suggestions_context)
        tbl_suggestions = table_suggestions()
        db_suggestions = database_suggestions()
        next_possible_keywords = detect_select_next_possible_keywords(suggestions_context)
        return [col_suggestions, tbl_suggestions, db_suggestions, next_possible_keywords]

    return []

def smart_suggestions(ast_, last_node_, prefix_):
    global ast
    global last_node
    global prefix
    ast = ast_
    last_node = last_node_
    prefix = prefix_

    suggestions = []
    if isinstance(ast, (Ast.Op, Ast.Expression)):
        return []

    if isinstance(ast, Ast.Statement):
        if ast.type == 'select':
            return select_suggestions()
