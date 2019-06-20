from pygments import highlight
from pygments.lexers import MySqlLexer
from pygments.token import Punctuation, Whitespace, Error, Text, Comment, \
        Operator, Keyword, Name, String, Number, Generic
from pygments.formatter import Formatter
from pygments.formatters import TerminalFormatter
import urwid

class UrwidWriter:
    def __init__(self):
        self.data = []

    def write(self, data):
        self.data.append(data)

class UrwidFormatter(Formatter):

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

code = 'SELECT DATE(value), MAX(1) FROM db.sometable JOIN db.other ON sometable.id = other.id WHERE x = \'1\' GROUP BY db.sometable.col2 ORDER BY col LIMIT 5'
writer = UrwidWriter()
# print(highlight(code, MySqlLexer(), TerminalFormatter()))
highlight(code, MySqlLexer(), UrwidFormatter(), writer)
print(writer.data)

filler = urwid.Filler(urwid.Text(writer.data))

palette = [
        ('sql:default', '', ''),
        ('sql:keyword', 'dark cyan', ''),
        ('sql:function', 'dark cyan', ''),
        ('sql:name', 'light gray', ''),
        ('sql:punctuation', 'yellow', ''),
        ('sql:number', 'dark green', ''),
        ('sql:operator', '', ''),
        ('sql:string', 'light cyan', ''),
        ('sql:keyword.type', 'dark cyan', ''),
        ('sql:builtin', 'dark cyan', ''),
        ]

l = urwid.MainLoop(filler, palette=palette)
l.run()
