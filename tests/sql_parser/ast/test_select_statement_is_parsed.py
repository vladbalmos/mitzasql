import pudb
import pytest
from mitzasql.sql_parser.parser import parse

def test_simple_select_stmt_is_parsed():
    raw_sql = '''

# SELECT
# tbl.col,
# 1 + 2,
# 1 * (2 + 3) ^ LEFT(tbl.col)

    # into outfile 'filename'
        # character set 'utf8'
    # columns terminated by 'string'
        # enclosed by 'char'
        # escaped by 'char'

# from table
# straight_join table3 t1
# straight_join table4 t2 on t1.id = t2.id
# join table5 on t2.customer_id = table5.id
# left outer join table6 using (col1)
# join table6 using (col4)


# where
    # table.id is not null
    # and
    # `date` between a and b

# group by t1 asc, t2 asc, t3 with rollup

# having 1 + 2 > 2

# order by t1.col asc,  t2.ccol, t3 desc, (1 + 2 / 3), fn(1 + 2)

# limit 1 offset 2

# procedure call(test, '123123')

# into dumpfile 'test'

# lock in share mode

# select a

# union

# select 1

# union (select 2)

# union
# (select a from b)

select 
1,
2,
(select 3)
'''

    ast = parse(raw_sql)
