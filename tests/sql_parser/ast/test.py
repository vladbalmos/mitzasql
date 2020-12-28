import pytest
from mitzasql.sql_parser.parser import parse

def test():
    raw_sql = '''

1 * 2 + left("dasdas", 1, 2) ^ 4

row (a, b)

match (a, v, 3) against ('something' in boolean mode)

'''
    ast = parse(raw_sql)
