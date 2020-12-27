import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer

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
    assert (Token.Number.Hex, '1') not in tokens
    assert (Token.Number.Hex, '20.321') not in tokens
    assert (Token.Number.Hex, '102e10') not in tokens
    assert (Token.Number.Hex, '0x12af') in tokens
    assert (Token.Number.Hex, '0X12af') not in tokens
    assert (Token.Number.Hex, '0x12gh') not in tokens
    assert (Token.Number.Hex, "x'fff'") in tokens
    assert (Token.Number.Hex, 'x"aaa"') not in tokens
    assert (Token.Number.Hex, "x'123j'") not in tokens
    assert (Token.Number.Hex, "X'fff'") in tokens
    assert (Token.Number.Hex, 'X"aaa"') not in tokens
    assert (Token.Number.Hex, "X'123j'") not in tokens
    assert (Token.Number.Hex, "x'fff") not in tokens
