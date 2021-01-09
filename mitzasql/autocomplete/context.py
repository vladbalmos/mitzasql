import mitzasql.sql_parser.ast as ast

def detect_context(ast_node, is_child=True):
    if ast_node is None:
        return

    node_type = ast_node.type
    node_value = ast_node.value or ''
    node_value = ast_node_value.lower()

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

    return detect_context(node.parent, is_child=False)

