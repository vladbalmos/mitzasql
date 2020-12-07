from mitzasql.sql_parser import parser

if __name__ == '__main__':
    sql = '''
SELECT
ALL DISTINCT DISTINCTROW HIGH_PRIORITY STRAIGHT_JOIN
SQL_NO_CACHE SQL_CALC_FOUND_ROWS SQL_BUFFER_RESULT SQL_BIG_RESULT
SQL_SMALL_RESULT
    @something,
    -1,
    .2e3,
    012312,
    12312.321312,
    312312e23,
    4322.2312312e10,
    X01AF,
    X'01AF',
    x'01af',
    0x01af,
    +1 AS c,
    2 + 5 b,
    1,
    "a' '\\" `",
    'a" "\\' `',
    `name`,
    LEFT(id, 3) d,
    RIGHT(another_table.id) X,
    id as full_id,
    (select first_name from actor where left(a) == 'b' limit 1) A,
    (select first_name from actor limit 1) as B
FROM
    actor
WHERE
    id = 2
    AND
    FROM_UNIXTIME(date) > 12312312
    OR
    num <>! x
ORDER BY name DESC
GROUP BY id
HAVING x > 5
'''

    tokens = parser.Parser(sql).parse()
