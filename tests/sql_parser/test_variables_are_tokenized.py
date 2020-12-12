import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer

def test_variables_are_tokenized():
    raw = '''
@variable,
@'single quoted variable',
@"double quoted variable",
@`backtick quoted variable`
@@is this a variable
'''
    tokens = list(Lexer(raw).tokenize())
    assert (Token.Variable, '@variable') in tokens
    assert (Token.Variable, "@'single quoted variable'") in tokens
    assert (Token.Variable, '@"double quoted variable"') in tokens
    assert (Token.Variable, '@`backtick quoted variable`') in tokens
