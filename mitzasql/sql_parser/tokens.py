# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

# This tokens implementation is heavily based on the python-sqlparse.tokens
# module https://github.com/andialbrecht/sqlparse which in turn was based
# on the pygment's token system
# See the sqlparse-LICENSE and sqlparse-AUTHORS files.
#
# Original python-sqlparse copyright notice:
## Copyright (C) 2009-2020 the sqlparse authors and contributors
## <see sqlparse-authoris file>
##
## This module is part of python-sqlparse and is released under
## the BSD License: https://opensource.org/licenses/BSD-3-Clause
##
## The Token implementation is based on pygment's token system written
## by Georg Brandl.
## http://pygments.org/

class _TokenType(tuple):
    parent = None

    def __contains__(self, item):
        return item is not None and (self is item or item[:len(self)] == self)

    def __getattr__(self, name):
        new = _TokenType(self + (name,))
        setattr(self, name, new)
        new.parent = self
        return new

    def __repr__(self):
        # self can be False only if its the `root` i.e. Token itself
        return 'Token' + ('.' if self else '') + '.'.join(self)


Token = _TokenType()

# Punctuation tokens
Punctuation = Token.Punctuation
Dot = Punctuation.Dot
Comma = Punctuation.Comma
Semicolon = Punctuation.Semicolon

# Literal
Literal = Token.Literal

# Numbers
Number = Token.Literal.Number
Number.Dec = Token.Literal.Number.Dec
Number.Bit = Token.Literal.Number.Bit
Number.Hex = Token.Literal.Number.Hex

# String
String = Token.Literal.String

# Boolean
Boolean = Token.Literal.Boolean

# Null
Null = Token.Literal.Null

# Whitespace
Whitespace = Token.Whitespace

# Operator
Operator = Token.Operator
Operator.Symbol = Token.Operator.Symbol

# Variable
Variable = Token.Variable

# Comment
Comment = Token.Comment

# Function
Function = Token.Function

# Keyword
Keyword = Token.Keyword
Reserved = Keyword.Reserved

# Misc
Name = Token.Name
Other = Token.Other
ParamMarker = Token.ParamMarker
Paren = Token.Paren
