import pytest
from mitzasql.sql_parser.parser import parse

def test():
    raw_sql = '''

1 between 2 and 3 is not false
'''
    ast = parse(raw_sql)
