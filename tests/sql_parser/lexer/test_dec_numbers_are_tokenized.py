import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer

def test_decimal_numbers_are_tokenized():
    raw = '''
-1,
20.321,
102e10
2312.123e-15,
-123312.123e-1
102e,
.203
1e20e30
120a30
'''
    tokens = list(Lexer(raw).tokenize())
    assert (Token.Number.Dec, '1') in tokens
    assert (Token.Number.Dec, '20.321') in tokens
    assert (Token.Number.Dec, '102e10') in tokens
    assert (Token.Number.Dec, '2312.123e-15') in tokens
    assert (Token.Number.Dec, '123312.123e-1') in tokens
    assert (Token.Number.Dec, '102e') not in tokens
    assert (Token.Number.Dec, '.203') in tokens
    assert (Token.Number.Dec, '1e20e30') not in tokens
    assert (Token.Number.Dec, '120a30') not in tokens
