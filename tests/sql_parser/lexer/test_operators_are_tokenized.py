import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer

def test_operators_are_tokenized():
    raw = '''
    ->>,
    <=>,
    >>,
    >=,
    <>,
    !=,
    <<,
    <=,
    ->,
    :=,
    ||,
    &&,
    &,
    >,
    <,
    %,
    *,
    +,
    -,
    -,
    /,
    =,
    =,
    ^,
    |,
    ~

    and
    between
    binary
    case
    div

    is
    not
    like
    mod
    regexp

    or
    rlike
    sounds
    xor

    # invalid operators
    :==
    *=
    >>>

'''
    tokens = list(Lexer(raw).tokenize())
    assert (Token.Operator.Symbol, '->>') in tokens
    assert (Token.Operator.Symbol, '<=>') in tokens
    assert (Token.Operator.Symbol, '>>') in tokens
    assert (Token.Operator.Symbol, '>=') in tokens
    assert (Token.Operator.Symbol, '<>') in tokens
    assert (Token.Operator.Symbol, '!=') in tokens
    assert (Token.Operator.Symbol, '<<') in tokens
    assert (Token.Operator.Symbol, '<=') in tokens
    assert (Token.Operator.Symbol, '->') in tokens
    assert (Token.Operator.Symbol, ':=') in tokens
    assert (Token.Operator.Symbol, '||') in tokens
    assert (Token.Operator.Symbol, '&&') in tokens
    assert (Token.Operator.Symbol, '&') in tokens
    assert (Token.Operator.Symbol, '>') in tokens
    assert (Token.Operator.Symbol, '<') in tokens
    assert (Token.Operator.Symbol, '%') in tokens
    assert (Token.Operator.Symbol, '*') in tokens
    assert (Token.Operator.Symbol, '+') in tokens
    assert (Token.Operator.Symbol, '-') in tokens
    assert (Token.Operator.Symbol, '-') in tokens
    assert (Token.Operator.Symbol, '/') in tokens
    assert (Token.Operator.Symbol, '=') in tokens
    assert (Token.Operator.Symbol, '=') in tokens
    assert (Token.Operator.Symbol, '^') in tokens
    assert (Token.Operator.Symbol, '|') in tokens
    assert (Token.Operator.Symbol, '~') in tokens

    assert (Token.Operator.Symbol, ':==') not in tokens
    assert (Token.Operator.Symbol, '*=') not in tokens
    assert (Token.Operator.Symbol, '>>>') not in tokens

    assert (Token.Operator, 'and') in tokens
    assert (Token.Operator, 'between') in tokens
    assert (Token.Operator, 'case') in tokens
    assert (Token.Operator, 'div') in tokens
    assert (Token.Operator, 'is') in tokens
    assert (Token.Operator, 'not') in tokens
    assert (Token.Operator, 'like') in tokens
    assert (Token.Operator, 'mod') in tokens
    assert (Token.Operator, 'regexp') in tokens
    assert (Token.Operator, 'or') in tokens
    assert (Token.Operator, 'rlike') in tokens
    assert (Token.Operator, 'sounds') in tokens
    assert (Token.Operator, 'xor') in tokens
