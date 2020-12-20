import pytest
from mitzasql.sql_parser.parser import parse

def test():
    raw_sql = '''

1 + 1 * 2 + -3 / 20

'''
# 11++1-
    # raw_sql = '''

# 1 + 1 * 2 - 10 + 2

# '''
    ast = parse(raw_sql)
