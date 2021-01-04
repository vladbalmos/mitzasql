import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer
from mitzasql.utils import token_is_parsed

def test_hex_numbers_are_tokenized():
    raw = '''
-1,
20.321,
102e10
0x12af
0X12af
0x12gh
x'fff'
x"aaa"
x'123j'
X'fff'
X"aaa"
X'123j'
x'fff
'''
    tokens = list(Lexer(raw).tokenize())
    assert not token_is_parsed((Token.Number.Hex, '1'), tokens)
    assert not token_is_parsed((Token.Number.Hex, '20.321'), tokens)
    assert not token_is_parsed((Token.Number.Hex, '102e10'), tokens)
    assert token_is_parsed((Token.Number.Hex, '0x12af'), tokens)
    assert not token_is_parsed((Token.Number.Hex, '0X12af'), tokens)
    assert not token_is_parsed((Token.Number.Hex, '0x12gh'), tokens)
    assert token_is_parsed((Token.Number.Hex, "x'fff'"), tokens)
    assert not token_is_parsed((Token.Number.Hex, 'x"aaa"'), tokens)
    assert not token_is_parsed((Token.Number.Hex, "x'123j'"), tokens)
    assert token_is_parsed((Token.Number.Hex, "X'fff'"), tokens)
    assert not token_is_parsed((Token.Number.Hex, 'X"aaa"'), tokens)
    assert not token_is_parsed((Token.Number.Hex, "X'123j'"), tokens)
    assert not token_is_parsed((Token.Number.Hex, "x'fff"), tokens)
