# Copyright (c) 2019 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from pygments.lexers import MySqlLexer
from pygments.token import Punctuation, Whitespace, Error, Text, Comment, \
        Operator, Keyword, Name, String, Number, Generic
from pygments.formatter import Formatter
import pygments

class UrwidSqlFormatter(Formatter):
    '''
    Provides syntax highligting for SQL using urwid display attributes
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.colorscheme = {
            Text: 'sql:default',
            Comment.Single: 'sql:comment.single',
            Comment.Multiline: 'sql:comment.multiline',
            Name.Builtin: 'sql:builtin',
            Name.Builtin.Pseudo: 'sql:builtin',
            Name.Attribute: 'sql:name',
            Name.Variable: 'sql:variable',
            Name: 'sql:name',
            Name.Function: 'sql:function',
            Keyword: 'sql:keyword',
            Keyword.Type: 'sql:keyword.type',
            Operator: 'sql:operator',
            Number.Float: 'sql:number',
            Number.Integer: 'sql:number',
            String.Single: 'sql:string',
            String.Affix: 'sql:string',
            String.Name: 'sql:string',
            Punctuation: 'sql:punctuation'
        }

    def format(self, tokensource, outfile):
        for ttype, value in tokensource:
            try:
                style = self.colorscheme[ttype]
            except KeyError:
                style = 'sql:default'

            outfile.write((style, value))

class UrwidTextWriter:
    '''
    Used by the formatter to write the formatted tokens
    '''
    def __init__(self):
        self.data = []

    def write(self, text_attr):
        self.data.append(text_attr)

    def clear(self):
        self.data = []

lexer = MySqlLexer(stripnl=False, stripall=False, ensurenl=False)
formatter = UrwidSqlFormatter()
writer = UrwidTextWriter()

def highlight(text):
    writer.clear()
    pygments.highlight(text, lexer, formatter, writer)

    return writer.data
