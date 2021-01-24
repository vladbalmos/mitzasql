import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer
from mitzasql.utils import token_is_parsed

def test_variables_are_tokenized():
    raw = '''
@@GLOBAL.g,
@@SESSION.s,
@@LOCAL.l,
@variable,
@'single quoted variable',
@"double quoted variable",
@`backtick quoted variable`
@@global
'''
    tokens = list(Lexer(raw).tokenize())
    assert token_is_parsed((Token.Variable, '@@GLOBAL.g'), tokens)
    assert token_is_parsed((Token.Variable, '@@SESSION.s'), tokens)
    assert token_is_parsed((Token.Variable, '@@LOCAL.l'), tokens)
    assert token_is_parsed((Token.Variable, '@variable'), tokens)
    assert token_is_parsed((Token.Variable, "@'single quoted variable'"), tokens)
    assert token_is_parsed((Token.Variable, '@"double quoted variable"'), tokens)
    assert token_is_parsed((Token.Variable, '@`backtick quoted variable`'), tokens)
    assert token_is_parsed((Token.Variable, '@@global'), tokens)
