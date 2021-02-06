# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .query_editor import QueryEditor
from ...logger import logger
from .. import utils

class SuggestionsWidget(urwid.Columns):
    def __init__(self):
        super().__init__([], dividechars=1)
        self._last_suggestions = None

    def populate(self, suggestions, index):
        if not suggestions:
            self.clear()
            self._append(u'No suggestions found')
            return

        if self._last_suggestions == suggestions and len(self.contents):
            self._highlight_suggestion(index)
            return

        counter = 0
        for item in suggestions:
            if counter == index:
                style = 'suggestion:highlight'
            else:
                style = 'suggestion'
            self._append(item, style)
            counter += 1

        self._last_suggestions = suggestions

    def _highlight_suggestion(self, index):
        counter = 0
        for col in self.contents:
            text, attr = utils.orig_w(col[0]).get_text()
            if counter != index:
                attr = 'suggestion'
            else:
                attr = 'suggestion:highlight'
            utils.orig_w(col[0]).set_text((attr, text))
            counter += 1


    def _append(self, item, style='suggestion'):
        self.contents.append((urwid.AttrMap(urwid.Text(item), style),
            self.options('given', len(item), False)))

    def clear(self):
        self.contents.clear()

class QueryWidget(urwid.AttrMap):
    SIGNAL_LOADING_SUGGESTIONS = 'loading_suggestions'
    SIGNAL_LOADED_SUGGESTIONS = 'loaded_suggestions'

    def __init__(self, autocomplete_engine=None):
        editor = QueryEditor(autocomplete_engine)
        container = urwid.Filler(urwid.AttrMap(editor, ''), valign='top')
        title = u'[F9: Run. Ctrl-F9: Clear. Esc: Close. Ctrl-P/Ctrl-N: Query history. Ctrl-Shift-Up/Down: Resize editor.]'

        self._suggestions_widget = SuggestionsWidget()

        frame = urwid.Frame(body=container, footer=self._suggestions_widget)
        line_box = urwid.LineBox(frame, title=title,
                title_align='right')

        urwid.connect_signal(editor, editor.SIGNAL_LOADING_SUGGESTIONS, self._loading_suggestions)
        urwid.connect_signal(editor, editor.SIGNAL_SHOW_SUGGESTIONS, self._show_suggestions)
        urwid.connect_signal(editor, editor.SIGNAL_HIDE_SUGGESTIONS, self._hide_suggestions)

        super().__init__(line_box, 'linebox')
        urwid.register_signal(self.__class__, [self.SIGNAL_LOADING_SUGGESTIONS, self.SIGNAL_LOADED_SUGGESTIONS])

    def _loading_suggestions(self, emitter):
        urwid.emit_signal(self, self.SIGNAL_LOADING_SUGGESTIONS, self)

    def _show_suggestions(self, emitter, suggestions, index=-1):
        urwid.emit_signal(self, self.SIGNAL_LOADED_SUGGESTIONS, self)
        self._suggestions_widget.populate(suggestions, index)

    def _hide_suggestions(self, emitter):
        urwid.emit_signal(self, self.SIGNAL_LOADED_SUGGESTIONS, self)
        self._suggestions_widget.clear()

    @property
    def query(self):
        return utils.orig_w_recursive(self.base_widget.body).edit_text

    @query.setter
    def query(self, query):
        utils.orig_w_recursive(self.base_widget.body).edit_text = query

    def clear(self):
        utils.orig_w_recursive(self.base_widget.body).edit_text = ''

    def keypress(self, size, key):
        key = super().keypress(size, key)
        # Disable the up key. It interferes with the parent pile container
        if key == 'up':
            return None
        return key
