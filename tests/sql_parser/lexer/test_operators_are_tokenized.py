import pytest
import mitzasql.sql_parser.tokens as Token
from mitzasql.sql_parser.lexer import Lexer
from mitzasql.utils import token_is_parsed

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
    assert token_is_parsed((Token.Operator.Symbol, '->>'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '<=>'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '>>'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '>='), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '<>'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '!='), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '<<'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '<='), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '->'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, ':='), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '||'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '&&'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '&'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '>'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '<'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '%'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '*'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '+'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '-'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '-'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '/'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '='), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '='), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '^'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '|'), tokens)
    assert token_is_parsed((Token.Operator.Symbol, '~'), tokens)

    assert not token_is_parsed((Token.Operator.Symbol, ':=='), tokens)
    assert not token_is_parsed((Token.Operator.Symbol, '*='), tokens)
    assert not token_is_parsed((Token.Operator.Symbol, '>>>'), tokens)

    assert token_is_parsed((Token.Operator, 'and'), tokens)
    assert token_is_parsed((Token.Operator, 'between'), tokens)
    assert token_is_parsed((Token.Operator, 'case'), tokens)
    assert token_is_parsed((Token.Operator, 'div'), tokens)
    assert token_is_parsed((Token.Operator, 'is'), tokens)
    assert token_is_parsed((Token.Operator, 'not'), tokens)
    assert token_is_parsed((Token.Operator, 'like'), tokens)
    assert token_is_parsed((Token.Operator, 'mod'), tokens)
    assert token_is_parsed((Token.Operator, 'regexp'), tokens)
    assert token_is_parsed((Token.Operator, 'or'), tokens)
    assert token_is_parsed((Token.Operator, 'rlike'), tokens)
    assert token_is_parsed((Token.Operator, 'sounds'), tokens)
    assert token_is_parsed((Token.Operator, 'xor'), tokens)
