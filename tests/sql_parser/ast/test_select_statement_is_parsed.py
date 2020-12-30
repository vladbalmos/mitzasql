import pudb
import pytest
from mitzasql.sql_parser.parser import parse

def test_simple_select_stmt_is_parsed():
    raw_sql = '''

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
straight_join table3 t1
straight_join table4 t2 on t1.id = t2.id
join table5 on t2.customer_id = table5.id
left outer join table6 using (col1)
join table6 using (col4)


where
    tbl.id is not null
    and
    `date` between a and b
'''

    ast = parse(raw_sql)
