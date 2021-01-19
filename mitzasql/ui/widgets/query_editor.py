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

import urwid

from .emacs_edit import EmacsEdit
from mitzasql.ui.syntax_highlight import highlight
from mitzasql.logger import logger
import pudb

class QueryEditor(EmacsEdit):
    SIGNAL_SHOW_SUGGESTIONS = 'show_suggestions'
    SIGNAL_HIDE_SUGGESTIONS = 'hide_suggestions'

    def __init__(self, autocomplete_engine):
        super().__init__(multiline=True, allow_tab=True)
        self._autocomplete_engine = autocomplete_engine
        self._suggestion_index = -1
        self._last_autocomplete_text_pos = None
        self._start_autocomplete_markers = [' ', '\t', '.', '(', '`', '*']
        urwid.register_signal(self.__class__, [self.SIGNAL_SHOW_SUGGESTIONS,
            self.SIGNAL_HIDE_SUGGESTIONS])

    def _should_autocomplete(self, key):
        if key != 'tab' and key != 'shift tab':
            return False

        if self.edit_pos == 0:
            return False

        prev_char = self.edit_text[self.edit_pos - 1]

        if prev_char in self._start_autocomplete_markers:
            return True

        word_separators = self._autocomplete_engine.get_word_separators()

        return prev_char not in word_separators

    def _autocomplete_direction(self, key):
        if key == 'tab':
            return 'forward'

        if key == 'shift tab':
            return 'back'

        raise RuntimeError(f'Invalid autocomplete key {key}')

    def _autocomplete(self, direction):
        if not self._last_autocomplete_text_pos:
            self._last_autocomplete_text_pos = self.edit_pos
            self._suggestion_index = -1

        suggestions = self._autocomplete_engine.get_suggestions(self.edit_text, self._last_autocomplete_text_pos)
        if not suggestions:
            return

        suggestions, prefix = suggestions

        try:
            index = self._get_suggestion_index(direction, len(suggestions))
            suggestion = suggestions[index]
        except IndexError:
            urwid.emit_signal(self, self.SIGNAL_SHOW_SUGGESTIONS, self, [])
            return

        if prefix.isupper():
            suggestion = suggestion.upper()

        middle_pos = self._last_autocomplete_text_pos
        after_suggestion_pos = self.edit_pos
        word_separators = self._autocomplete_engine.get_word_separators()

        while after_suggestion_pos <= len(self.edit_text) - 1:
            char = self.edit_text[after_suggestion_pos]
            if char in word_separators:
                break
            after_suggestion_pos += 1

        text = self.edit_text[0:middle_pos] + suggestion[len(prefix):] + self.edit_text[after_suggestion_pos:]
        self.edit_text = text
        self.edit_pos = middle_pos + len(suggestion[len(prefix):])
        urwid.emit_signal(self, self.SIGNAL_SHOW_SUGGESTIONS, self, suggestions, index)

    def _get_suggestion_index(self, direction, suggestions_len):
        if direction == 'forward':
            increment = 1
        else:
            increment = -1

        self._suggestion_index += increment

        if self._suggestion_index < 0:
            self._suggestion_index = suggestions_len - 1
        elif self._suggestion_index >= suggestions_len:
            self._suggestion_index = 0

        return self._suggestion_index

    def keypress(self, size, key):
        if self._should_autocomplete(key):
            direction = self._autocomplete_direction(key)
            self._autocomplete(direction)
            return None

        self._last_autocomplete_text_pos = None
        urwid.emit_signal(self, self.SIGNAL_HIDE_SUGGESTIONS, self)
        return super().keypress(size, key)

    def render(self, size, focus=False):
        (maxcol,) = size
        self._shift_view_to_cursor = bool(focus)

        text = highlight(self._edit_text)
        if not len(text):
            text = u''

        canv = urwid.Text(text).render((maxcol,))
        if focus:
            canv = urwid.CompositeCanvas(canv)
            canv.cursor = self.get_cursor_coords((maxcol,))
        return canv
