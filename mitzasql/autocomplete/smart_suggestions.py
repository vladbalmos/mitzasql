from mitzasql.utils import dfs
from mitzasql.db.model import *
import mitzasql.sql_parser.ast as Ast
import mitzasql.sql_parser.tokens as Token
import pudb

model = None
ast = None
last_node = None

def set_smart_suggestions_model(sql_model):
    global model
    model = sql_model

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

    if node_type == 'where' or node_type == 'having':
        return node_type

    if node_type == 'modifier':
        return 'select_modifier'

    if node_type == 'charset':
        return 'charset'

    if node_type == 'variable':
        return 'variable'

    return detect_select_context(ast_node.parent, is_child=False)

def table_name_from_alias(alias):
    # TODO extract table name from alias
    return alias

def format_model_columns():
    cols = model.columns
    cols_list = []
    for col in cols:
        cols_list.append(col['name'])

    return cols_list

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
        suggestions.append(row[0])

    return suggestions


def column_suggestions():
    suggestions = []
    table_name = None
    if last_node.parent and last_node.parent.type == 'identifier':
        table_name = table_name_from_alias(last_node.parent.value)
        return table_columns_suggestions(table_name)

    if table_name is None:
        if isinstance(model, TableModel):
            return format_model_columns()

    return table_suggestions()


def table_suggestions():
    suggestions = []
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
        print(e)
        return []

    data = cursor.fetchall()
    for row in data:
        suggestions.append(row[0])

    return suggestions

def select_suggestions():
    if last_node is None:
        return []

    suggestions_context = detect_select_context(last_node)
    if suggestions_context is None:
        return []

    if suggestions_context == 'column':
        return column_suggestions()

    if suggestions_context == 'table':
        return table_suggestions()

    return []

def smart_suggestions(ast_, last_node_):
    global ast
    global last_node
    ast = ast_
    last_node = last_node_

    suggestions = []
    if isinstance(ast, (Ast.Op, Ast.Expression)):
        return []

    if isinstance(ast, Ast.Statement):
        if ast.type == 'select':
            return select_suggestions()
