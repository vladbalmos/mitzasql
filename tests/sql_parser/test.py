import pytest
from mitzasql.sql_parser.parser import parse

def test():
    raw_sql = '''

# 1 or 2
# 1 || 2
# 1 xor 2
# 1 and 2
# 1 && 2
# not 1
10 is true && ! 7 or 2 xor 4 or 3 is not false

'''
    ast = parse(raw_sql)
