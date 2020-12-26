import pytest
from mitzasql.sql_parser.parser import parse

def test():
    raw_sql = '''

'''
    ast = parse(raw_sql)
