import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer
from mitzasql.utils import token_is_parsed

def test_schema_object_is_tokenized():
    raw = '''
`schema`.`object`
@`not a schema object`
'''
    tokens = list(Lexer(raw).tokenize())
    assert token_is_parsed((Token.Name, '`schema`'), tokens)
    assert token_is_parsed((Token.Name, '`object`'), tokens)
    assert not token_is_parsed((Token.Name, '`not a schema object`'), tokens)
