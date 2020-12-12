import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer

def test_single_quote_string_is_tokenized():
    raw = '''
'this is a string'
'''
    tokens = list(Lexer(raw).tokenize())
    assert len(tokens) == 3
    assert tokens[1] == (Token.String, "'this is a string'")

def test_double_quote_string_is_tokenized():
    raw = '''
"this is a string"
'''
    tokens = list(Lexer(raw).tokenize())
    assert len(tokens) == 3
    assert tokens[1] == (Token.String, '"this is a string"')

def test_multiple_strings_are_tokenized():
    raw = '''
"first string",
'second string' 'third string'|"fourth string" '
last string
'''
    tokens = list(Lexer(raw).tokenize())
    assert (Token.String, '"first string"') in tokens
    assert (Token.String, "'second string'") in tokens
    assert (Token.String, "'third string'") in tokens
    assert (Token.String, '"fourth string"') in tokens
    assert (Token.String, "'\nlast string\n") in tokens
