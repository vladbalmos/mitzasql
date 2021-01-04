import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer
from mitzasql.utils import token_is_parsed

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
    assert token_is_parsed((Token.Number.Dec, '1'), tokens)
    assert token_is_parsed((Token.Number.Dec, '20.321'), tokens)
    assert token_is_parsed((Token.Number.Dec, '102e10'), tokens)
    assert token_is_parsed((Token.Number.Dec, '2312.123e-15'), tokens)
    assert token_is_parsed((Token.Number.Dec, '123312.123e-1'), tokens)
    assert not token_is_parsed((Token.Number.Dec, '102e'), tokens)
    assert token_is_parsed((Token.Number.Dec, '.203'), tokens)
    assert not token_is_parsed((Token.Number.Dec, '1e20e30'), tokens)
    assert not token_is_parsed((Token.Number.Dec, '120a30'), tokens)
