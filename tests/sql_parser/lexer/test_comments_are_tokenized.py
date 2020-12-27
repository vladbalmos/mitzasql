import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer

def test_hash_comment_is_tokenized():
    raw = '''
# this is a comment
this is not a comment
'''
    tokens = list(Lexer(raw).tokenize())
    assert (Token.Comment, '# this is a comment\n') in tokens

def test_c_style_comment_is_tokenized():
    raw = '''
/* this is a c style comment */
/* unterminated comment
'''
    tokens = list(Lexer(raw).tokenize())
    assert (Token.Comment, '/* this is a c style comment */') in tokens
    assert (Token.Comment, '/* unterminated comment\n') in tokens

def test_hash_comment_is_tokenized():
    raw = '''
-- this is a comment
--this is not a comment
'''
    tokens = list(Lexer(raw).tokenize())
    assert (Token.Comment, '-- this is a comment\n') in tokens
    assert (Token.Comment, '--this is not a comment\n') not in tokens
