import sys
import mitzasql.sql_parser.tokens as Token

index = {}

data_types = {
    # numeric
    'bit': Token.Datatype,
    'tinyint': Token.Datatype,
    'bool': Token.Datatype,
    'boolean': Token.Datatype,
    'smallint': Token.Datatype,
    'mediumint': Token.Datatype,
    'int': Token.Datatype,
    'integer': Token.Datatype,
    'bigint': Token.Datatype,
    'decimal': Token.Datatype,
    'dec': Token.Datatype,
    'numeric': Token.Datatype,
    'fixed': Token.Datatype,
    'float': Token.Datatype,
    'double': Token.Datatype,
    'double_precision': Token.Datatype,
    'real': Token.Datatype,

    # date and time
    'date': Token.Datatype,
    'datetime': Token.Datatype,
    'timestamp': Token.Datatype,
    'time': Token.Datatype,
    'year': Token.Datatype,

    # string
    'char': Token.Datatype,
    'varchar': Token.Datatype,
    'binary': Token.Datatype,
    'varbinary': Token.Datatype,
    'blob': Token.Datatype,
    'text': Token.Datatype,
    'enum': Token.Datatype,
    'set': Token.Datatype,

    # spatial
    'geometry': Token.Datatype,
    'point': Token.Datatype,
    'linestring': Token.Datatype,
    'polygon': Token.Datatype,
    'multipoint': Token.Datatype,
    'multilinestring': Token.Datatype,
    'multipolygon': Token.Datatype,
    'geometrycollection': Token.Datatype,

    # json
    'json': Token.Datatype
}
index['data_types'] = data_types

symbol_operators = [
    '->>',
    '<=>',
    '>>',
    '>=',
    '<>',
    '!=',
    '<<',
    '<=',
    '->',
    ':=',
    '||',
    '&&',
    '&',
    '>',
    '<',
    '%',
    '*',
    '+',
    '-',
    '-',
    '/',
    '=',
    '=',
    '^',
    '|',
    '~'
]
word_operators = {
    'and': Token.Operator,
    'between': Token.Operator,
    'case': Token.Operator,
    'div': Token.Operator,

    'is': Token.Operator,
    'not': Token.Operator,
    'like': Token.Operator,
    'mod': Token.Operator,
    'regexp': Token.Operator,

    'or': Token.Operator,
    'rlike': Token.Operator,
    'sounds': Token.Operator,
    'xor': Token.Operator,
}
index['word_operators'] = word_operators

function_operators = {
    'coalesce': Token.Operator,
    'greatest': Token.Operator,
    'in': Token.Operator,
    'interval': Token.Operator,

    'isnull': Token.Operator,
    'least': Token.Operator,
    'strcmp': Token.Operator
}
index['function_operators'] = word_operators

flow_control_functions = {
    'if': Token.FlowControl,
    'ifnull': Token.FlowControl,
    'nullif': Token.FlowControl
}
index['flow_control_functions'] = flow_control_functions

keywords = {
    'when': Token.Keyword,
    'then': Token.Keyword,
    'else': Token.Keyword,
    'end': Token.Keyword
}
index['keyword'] = keywords

literals = {
    'false': Token.Boolean,
    'true': Token.Boolean,
    'null': Token.Null
}
index['literals'] = literals

def classify(keyword):
    for keyword_dict in index:
        try:
            return index[keyword_dict][keyword.lower()]
        except KeyError:
            continue

    return Token.Name

