import pytest
from mitzasql.sql_parser.parser import parse

def test():
    raw_sql = '''

1 + 1 * 2 - 10 + 2

'''
#112*+10-
    ast = parse(raw_sql)
