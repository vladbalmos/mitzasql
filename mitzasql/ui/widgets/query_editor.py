# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .emacs_edit import EmacsEdit
from ..syntax_highlight import highlight
from ...logger import logger
from .. import clipboard

class QueryEditor(EmacsEdit):
    SIGNAL_LOADING_SUGGESTIONS = 'loading_suggestions'
    SIGNAL_SHOW_SUGGESTIONS = 'show_suggestions'
    SIGNAL_HIDE_SUGGESTIONS = 'hide_suggestions'

    def __init__(self, autocomplete_engine):
        super().__init__(multiline=True, allow_tab=True, wrap='space')
        self._autocomplete_engine = autocomplete_engine
        self._suggestion_index = -1
        self._suggestions_found = False
        self._last_autocomplete_text_pos = None
        self._start_autocomplete_markers = [' ', '\t', '.', '(', '`', '*']
        urwid.register_signal(self.__class__, [self.SIGNAL_LOADING_SUGGESTIONS, self.SIGNAL_SHOW_SUGGESTIONS, self.SIGNAL_HIDE_SUGGESTIONS])

    def _should_autocomplete(self, key):
        if key != 'tab' and key != 'shift tab':
            return False

        if self.edit_pos == 0:
            return False

        if self._suggestions_found:
            return True

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

        urwid.emit_signal(self, self.SIGNAL_LOADING_SUGGESTIONS, self)
        suggestions = self._autocomplete_engine.get_suggestions(self.edit_text, self._last_autocomplete_text_pos)
        if not suggestions:
            self._suggestions_found = False
            return

        suggestions, prefix = suggestions
        self._suggestions_found = bool(len(suggestions))

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

    def _copy_text(self):
        clipboard.copy(self.edit_text)

    def _paste_text(self):
        pasted_text = clipboard.paste()
        if not pasted_text:
            return

        text = self.edit_text[0:self.edit_pos]
        text += pasted_text
        text += self.edit_text[self.edit_pos:]
        self.set_edit_text(text)
        self.edit_pos += len(pasted_text)

    def keypress(self, size, key):
        if self._should_autocomplete(key):
            direction = self._autocomplete_direction(key)
            self._autocomplete(direction)
            return None

        if key == 'ctrl c':
            self._copy_text()
            return

        if key == 'ctrl v':
            self._paste_text()
            return

        self._last_autocomplete_text_pos = None
        self._suggestions_found = False
        urwid.emit_signal(self, self.SIGNAL_HIDE_SUGGESTIONS, self)
        return super().keypress(size, key)

    def render(self, size, focus=False):
        (maxcol,) = size
        self._shift_view_to_cursor = bool(focus)

        text = highlight(self.edit_text)
        if not len(text):
            text = u''

        canv = urwid.Text(text).render((maxcol,))
        if focus:
            canv = urwid.CompositeCanvas(canv)
            canv.cursor = self.get_cursor_coords((maxcol,))
        return canv
