# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

from pygments.lexers import MySqlLexer
from pygments.token import Punctuation, Whitespace, Error, Text, Comment, \
        Operator, Keyword, Name, String, Number, Generic, Literal
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
            String.Double: 'sql:string',
            String.Symbol: 'sql:string',
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
