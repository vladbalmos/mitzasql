import pudb
import pytest
from mitzasql.sql_parser.parser import parse

def test_simple_select_stmt_is_parsed():
    raw_sql = '''

# tbl.col

SELECT
tbl.col,
1 + 2,
1 * (2 + 3) ^ LEFT(tbl.col)

    into outfile 'filename'
        character set 'utf8'
    columns terminated by 'string'
        enclosed by 'char'
        escaped by 'char'

from table

'''

    ast = parse(raw_sql)
