import pytest
from mitzasql.sql_parser.parser import parse

def test():
    raw_sql = '''

1 + 1 * 2 - 10

'''
# 1+(1 * 2)
# 112*+
    ast = parse(raw_sql)
