# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

# Helper functions for determining the closest context which can
# yield autocomplete suggestions

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
        return ['order', 'by', 'limit']

    if context == 'order':
        return ['limit']

    return []

def detect_update_next_possible_keywords(context):
    if context == 'table':
        return ['set', 'where', 'by', 'order', 'limit']

    if context == 'assignment_list':
        return ['where', 'by', 'order', 'limit']

    if context == 'where':
        return ['by', 'order', 'limit']

    if context == 'order':
        return ['limit']

    return []

def detect_delete_next_possible_keywords(context):
    if context == 'table_references':
        return ['from', 'where', 'by', 'order', 'limit']

    if context == 'context':
        return ['using', 'where', 'by', 'order', 'limit']

    if context == 'where':
        return ['by', 'order', 'limit']

    if context == 'order':
        return ['limit']

    return []

def detect_call_context(ast_node):
    if ast_node is None:
        return

    node_type = ast_node.type
    node_value = ast_node.value or ''
    node_value = node_value.lower()

    if node_type == 'function':
        return 'arguments'

    if node_type == 'proc':
        return 'proc'

    return detect_call_context(ast_node.parent)

def detect_update_context(ast_node):
    if ast_node is None:
        return

    node_type = ast_node.type
    node_value = ast_node.value or ''
    node_value = node_value.lower()

    if node_type == 'assignment_list':
        return node_type

    if node_type == 'join_spec':
        return 'column'

    if node_type == 'table_references':
        return 'table'

    if node_type in ('where', 'order'):
        return node_type

    return detect_update_context(ast_node.parent)

def detect_insert_context(ast_node):
    if ast_node is None:
        return

    node_type = ast_node.type
    node_value = ast_node.value or ''
    node_value = node_value.lower()

    if node_type == 'assignment_list':
        return node_type

    if node_type == 'into':
        return 'table'

    if node_type == 'columns':
        return 'column'

    if node_type == 'update':
        return 'column'

    return detect_insert_context(ast_node.parent)

def detect_delete_context(ast_node):
    if ast_node is None:
        return

    node_type = ast_node.type
    node_value = ast_node.value or ''
    node_value = node_value.lower()

    if node_type == 'join_spec':
        return 'column'

    if node_type == 'table_references':
        return 'table_references'

    if node_type == 'from' or node_type == 'using':
        return 'table'

    if node_type in ('where', 'order'):
        return node_type

    return detect_delete_context(ast_node.parent)

def detect_select_context(ast_node):
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

    return detect_select_context(ast_node.parent)

def detect_set_context(ast_node):
    if ast_node is None:
        return

    node_type = ast_node.type
    node_value = ast_node.value or ''
    node_value = node_value.lower()

    if node_type == 'set' and ast_node.parent is None:
        return 'set'

    if node_type == 'character':
        return 'character'

    if node_type == 'variable':
        return 'variable'

    return detect_set_context(ast_node.parent)
