import urwid

from .query_editor import QueryEditor

class QueryWidget(urwid.AttrMap):
    def __init__(self):
        editor = QueryEditor()
        container = urwid.Filler(urwid.AttrMap(editor, ''), valign='top')
        title = u'[F9: Run. Ctrl-F9: Clear. Esc: Focus table. Ctrl-P/Ctrl-N: Query history]'
        line_box = urwid.LineBox(container, title=title,
                title_align='right')

        super().__init__(line_box, 'linebox')

    @property
    def query(self):
        return self.base_widget.edit_text

    @query.setter
    def query(self, query):
        self.base_widget.edit_text = query

    def clear(self):
        self.base_widget.edit_text = ''

    def keypress(self, size, key):
        key = super().keypress(size, key)
        # Disable the up key. It interferes with the parent pile container
        if key == 'up':
            return None
        return key
