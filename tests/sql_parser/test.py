import pytest
from mitzasql.sql_parser.parser import parse

def test():
    raw_sql = '''

1 <> 2 is not null

'''
    ast = parse(raw_sql)
