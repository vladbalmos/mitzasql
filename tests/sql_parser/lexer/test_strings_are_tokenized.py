import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer
from mitzasql.utils import token_is_parsed

def test_single_quote_string_is_tokenized():
    raw = '''
'this is a string'
'''
    tokens = list(Lexer(raw).tokenize())
    assert len(tokens) == 3
    assert tokens[1] == (Token.String, "'this is a string'", 1)

def test_double_quote_string_is_tokenized():
    raw = '''
"this is a string"
'''
    tokens = list(Lexer(raw).tokenize())
    assert len(tokens) == 3
    assert tokens[1] == (Token.String, '"this is a string"', 1)

def test_multiple_strings_are_tokenized():
    raw = '''
"first string",
'second string' 'third string'|"fourth string" '
last string
'''
    tokens = list(Lexer(raw).tokenize())
    assert token_is_parsed((Token.String, '"first string"'), tokens)
    assert token_is_parsed((Token.String, "'second string'"), tokens)
    assert token_is_parsed((Token.String, "'third string'"), tokens)
    assert token_is_parsed((Token.String, '"fourth string"'), tokens)
    assert token_is_parsed((Token.String, "'\nlast string\n"), tokens)

def test_doubled_quotes_count_as_an_escaped_quote():
    raw = '''
"encoded "" string",
'encoded '' string',
'''
    tokens = list(Lexer(raw).tokenize())
    assert token_is_parsed((Token.String, '"encoded " string"'), tokens)
    assert token_is_parsed((Token.String, "'encoded ' string'"), tokens)
