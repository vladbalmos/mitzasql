import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer
from mitzasql.utils import token_is_parsed

def test_single_quote_string_is_tokenized():
    raw = '''
dot. comma, semicolo;
'''
    tokens = list(Lexer(raw).tokenize())
    assert token_is_parsed((Token.Dot, '.'), tokens)
    assert token_is_parsed((Token.Comma, ','), tokens)
    assert token_is_parsed((Token.Semicolon, ';'), tokens)

def test_parens_are_tokenized():
    raw = '''
(dot.) comma(,) (semicolo;
'''
    tokens = Lexer(raw).tokenize()

    open_parens_count = 0
    closed_parens_count = 0
    for token in tokens:
        if token[0] == Token.Paren and token[1] == '(':
            open_parens_count += 1
            continue

        if token[0] == Token.Paren and token[1] == ')':
            closed_parens_count += 1
            continue

    assert open_parens_count == 3
    assert closed_parens_count == 2
