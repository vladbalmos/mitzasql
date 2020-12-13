import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer

def test_schema_object_is_tokenized():
    raw = '''
`schema`.`object`
@`not a schema object`
'''
    tokens = list(Lexer(raw).tokenize())
    assert (Token.Name, '`schema`') in tokens
    assert (Token.Name, '`object`') in tokens
    assert (Token.Name, '`not a schema object`') not in tokens