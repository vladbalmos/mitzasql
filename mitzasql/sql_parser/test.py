from mitzasql.sql_parser.lexer import Lexer

if __name__ == '__main__':
    # sql = '''
# SELECT
    # b'',
    # x'',
    # 0x,
    # 0B
# '''
    sql = '''
SELECT
ALL DISTINCT DISTINCTROW HIGH_PRIORITY STRAIGHT_JOIN
SQL_NO_CACHE SQL_CALC_FOUND_ROWS SQL_BUFFER_RESULT SQL_BIG_RESULT
SQL_SMALL_RESULT
    @something,
    @'something',
    @"something",
    @`something`,
    a <=>> b,
    a := b,
    a %= b,
    a *= b,
    a &>= b,
    a ->- b,
    a ->> b,
    a <=> b,
    a <=>> b,
    -1,
    .2e3,
    .2e-32,
    1e,
    .2e,
    012312,
    12312.321312,
    312312e23,
    4322.2312312e10,
    X01AF,
    X'01AF',
    x'01af',
    0xh1,
    0x01af,
    0b000,
    0b001,
    0b02,
    0B01,
    0ba,
    b'0101',
    b'0123',
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

# this is a comment
-- this is a comment
select
/* this is a comment */
/* this is 
also a comment*/
/**/
select
false,
FALSE,
true,
TRUE,
null
'''

    tokens = Lexer(sql).tokenize()
    for t in tokens:
        print(t)

