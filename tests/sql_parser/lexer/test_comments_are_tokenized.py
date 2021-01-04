import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer
from mitzasql.utils import token_is_parsed

def test_hash_comment_is_tokenized():
    raw = '''
# this is a comment
this is not a comment
'''
    tokens = list(Lexer(raw).tokenize())
    assert token_is_parsed((Token.Comment, '# this is a comment\n'), tokens)

def test_c_style_comment_is_tokenized():
    raw = '''
/* this is a c style comment */
/* unterminated comment
'''
    tokens = list(Lexer(raw).tokenize())
    assert token_is_parsed((Token.Comment, '/* this is a c style comment */'), tokens)
    assert token_is_parsed((Token.Comment, '/* unterminated comment\n'), tokens)

def test_hash_comment_is_tokenized():
    raw = '''
-- this is a comment
--this is not a comment
'''
    tokens = list(Lexer(raw).tokenize())
    assert token_is_parsed((Token.Comment, '-- this is a comment\n'), tokens)
    assert not token_is_parsed((Token.Comment, '--this is not a comment\n'), tokens)
