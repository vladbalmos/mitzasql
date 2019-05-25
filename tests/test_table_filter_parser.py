import pytest

from mitzasql.table_filter_parser import Parser

def test_parser():
    p = Parser("1 2")
    tokens = p.parse()
    assert tokens[0] == '1'
    assert tokens[1] == '2'

    p = Parser("abc defg")
    tokens = p.parse()
    assert tokens[0] == 'abc'
    assert tokens[1] == 'defg'

    p = Parser("abc       defg")
    tokens = p.parse()
    assert tokens[0] == 'abc'
    assert tokens[1] == 'defg'

    p = Parser("  abc       defg")
    tokens = p.parse()
    assert tokens[0] == 'abc'
    assert tokens[1] == 'defg'

    p = Parser("  abc       defg  ")
    tokens = p.parse()
    assert tokens[0] == 'abc'
    assert tokens[1] == 'defg'

    p = Parser("abc       defg  ")
    tokens = p.parse()
    assert tokens[0] == 'abc'
    assert tokens[1] == 'defg'

    p = Parser("'abc   defg' 123")
    tokens = p.parse()
    assert tokens[0] == 'abc   defg'
    assert tokens[1] == '123'

    p = Parser("'abc   defg''123'")
    tokens = p.parse()
    assert tokens[0] == 'abc   defg123'

    p = Parser("'ab\\'c   defg' 123")
    tokens = p.parse()
    assert tokens[0] == 'ab\'c   defg'
    assert tokens[1] == '123'

    p = Parser('"ab\\"c   de\\"fg" 123')
    tokens = p.parse()
    assert tokens[0] == 'ab"c   de"fg'
    assert tokens[1] == '123'

    p = Parser('\\r')
    tokens = p.parse()
    assert tokens[0] == '\\r'

    p = Parser('\\r 123 \\n\\r\\tabc')
    tokens = p.parse()
    assert tokens[0] == '\\r'
    assert tokens[1] == '123'
    assert tokens[2] == '\\n\\r\\tabc'

    p = Parser("'2017-09-02 12:12:12' '2018-02-02 12:13:13'")
    tokens = p.parse()
    assert tokens[0] == '2017-09-02 12:12:12'
    assert tokens[1] == '2018-02-02 12:13:13'
