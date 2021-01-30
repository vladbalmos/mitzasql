import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer
from mitzasql.utils import token_is_parsed

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
    assert not token_is_parsed((Token.Number.Bit, '1'), tokens)
    assert not token_is_parsed((Token.Number.Bit, '20.321'), tokens)
    assert not token_is_parsed((Token.Number.Bit, '102e10'), tokens)
    assert token_is_parsed((Token.Number.Bit, '0b01'), tokens)
    assert not token_is_parsed((Token.Number.Bit, '0b02'), tokens)
    assert token_is_parsed((Token.Number.Bit, '0b111'), tokens)
    assert not token_is_parsed((Token.Number.Bit, '0B111'), tokens)
    assert token_is_parsed((Token.Number.Bit, "b'01'"), tokens)
    assert token_is_parsed((Token.Number.Bit, "B'01'"), tokens)
    assert not token_is_parsed((Token.Number.Bit, 'B"01"'), tokens)
    assert not token_is_parsed((Token.Number.Bit, '0b11b1'), tokens)
    assert not token_is_parsed((Token.Number.Bit, "b'2'"), tokens)
