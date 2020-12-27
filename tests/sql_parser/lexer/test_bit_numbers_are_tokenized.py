import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer

def test_bit_numbers_are_tokenized():
    raw = '''
-1,
20.321,
102e10
0b01
0b02
0b111
0B111
b'01'
B'01'
B"01"
0b11b1
b'2'
'''
    tokens = list(Lexer(raw).tokenize())
    assert (Token.Number.Bit, '1') not in tokens
    assert (Token.Number.Bit, '20.321') not in tokens
    assert (Token.Number.Bit, '102e10') not in tokens
    assert (Token.Number.Bit, '0b01') in tokens
    assert (Token.Number.Bit, '0b02') not in tokens
    assert (Token.Number.Bit, '0b111') in tokens
    assert (Token.Number.Bit, '0B111') not in tokens
    assert (Token.Number.Bit, "b'01'") in tokens
    assert (Token.Number.Bit, "B'01'") in tokens
    assert (Token.Number.Bit, 'B"01"') not in tokens
    assert (Token.Number.Bit, '0b11b1') not in tokens
    assert (Token.Number.Bit, "b'2'") not in tokens
