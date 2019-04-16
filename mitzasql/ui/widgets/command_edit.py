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

class CommandEdit(EmacsEdit):
    '''Implement a basic VIM style command edit widget'''
    SIGNAL_CANCEL = 'cancel_edit'

    def __init__(self, command_processor):
        self._command_processor = command_processor
        self._marker = None
        super().__init__()
        urwid.register_signal(self.__class__, self.SIGNAL_CANCEL)

    def set_marker(self, marker):
        self.set_caption(marker)
        self._marker = marker

    def _show_prev_command(self):
        item = self._command_processor.history.prev
        if not item:
            return
        self.edit_text = item
        self.edit_pos = len(item)

    def _show_next_command(self):
        item = self._command_processor.history.next
        if not item:
            return
        self.edit_text = item
        self.edit_pos = len(item)

    def _cancel_edit(self):
        urwid.emit_signal(self, self.SIGNAL_CANCEL, self)

    def show_last_cmd(self):
        last_cmd = self._command_processor.history.last
        if not last_cmd:
            return
        self.edit_text = last_cmd
        self.edit_pos = len(last_cmd)

    def keypress(self, size, key):
        if (key == 'tab' or key == 'shift tab') and self._marker == ':':
            if key == 'shift tab':
                direction = 'back'
            else:
                direction = 'forward'
            if self._autocomplete(direction):
                return None

        if key != 'tab' and key != 'shift tab':
            self._autocomplete(reset=True)

        if key == 'esc':
            self._cancel_edit()
            return

        key = super().keypress(size, key)
        if key == 'enter':
            text = self.edit_text
            marker = self._marker
            self._cancel_edit()
            self._command_processor.execute(str_cmd_marker=marker,
                    cmd=text)
            return

        # Show previous command
        if key == 'ctrl p':
            self._show_prev_command()
            return

        # Show next command
        if key == 'ctrl n':
            self._show_next_command()
            return

        return key

    def _autocomplete(self, direction='forward', reset=False):
        if reset is True:
            self._command_processor.reset_autocomplete()
            return

        text = self.edit_text
        pos = self.edit_pos
        space_pos = text.find(' ')
        segments = text.split(' ')
        suggestion = None
        new_pos = None

        # Autocomplete first word
        if pos <= len(segments[0]):
            if pos <= space_pos or space_pos == -1:
                suggestion = self._command_processor.autocomplete(segments[0],
                        command=True, direction=direction)

            if suggestion:
                segments[0] = suggestion
                new_pos = len(suggestion)

        # Autocomplete second word
        if pos > space_pos and space_pos > -1:
            next_space_pos = text.find(' ', space_pos + 1)
            if pos > next_space_pos and next_space_pos > -1:
                return

            suggestion = self._command_processor.autocomplete(segments[1],
                    argument=True, command_name=segments[0],
                    direction=direction)
            if suggestion:
                segments[1] = suggestion
                new_pos = len(segments[0]) + len(suggestion) + 1

        if suggestion:
            text = ' '.join(segments)
            self.edit_text = text
            self.edit_pos = new_pos
            return True

    def reset(self):
        self._marker = ''
        self.set_caption('')
        self.edit_text = ''

