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

from mitzasql.history import History

class CommandError(Exception):
    pass

class Autocomplete:
    def __init__(self, suggestions, word):
        self._suggestions = suggestions
        self._suggestions.sort()
        self._index = None
        self._keyword = word
        self._matches = self._make_matches()
        self._last_dir = None

    def _make_matches(self):
        matches = []
        for sug in self._suggestions:
            if sug.lower().startswith(self._keyword.lower()):
                matches.append(sug)
        return matches

    def suggestion(self, direction):
        if self._last_dir is None:
            self._last_dir = direction
        else:
            if self._last_dir != direction:
                if direction == 'forward':
                    self._index += 2
                else:
                    self._index -= 2
            self._last_dir = direction

        if direction == 'forward':
            return self.next_suggestion()
        return self.prev_suggestion()

    def next_suggestion(self):
        if not len(self._matches):
            return None
        if self._index is None or self._index > len(self._matches) - 1:
            self._index = 0
        match = self._matches[self._index]
        self._index += 1
        return match

    def prev_suggestion(self):
        if not len(self._matches):
            return None
        if self._index is None or self._index < 0:
            self._index = len(self._matches) - 1

        match = self._matches[self._index]
        self._index -= 1
        return match

class BaseCmdProcessor:
    SIGNAL_ERROR = 'error'
    '''Support basic VIM style commands'''
    def __init__(self):
        self.history = History()
        self._cmd_strings = {}
        self.cmd_args_suggestions = {}
        self._colon_cmds = [
                ('q', 'quit', self._quit)
                ]
        self._cmd_keys = {}
        self._autocomplete = None
        urwid.register_signal(self.__class__, self.SIGNAL_ERROR)

    def is_string_comand(self, key):
        return key in self._cmd_strings

    def is_key_command(self, key):
        return key in self._cmd_keys

    def colon_handler(self, cmd):
        self.history.append(cmd)
        if not cmd or len(cmd) == 0:
            return

        cmd, *args = cmd.split(' ')
        for colon_cmd in self._colon_cmds:
            if cmd not in colon_cmd[0:-1]:
                continue
            handler = colon_cmd[-1]
            return handler(*args)

        self._emit_error(u'Command not found!')

    def execute(self, cmd_key=None, str_cmd_marker=None, cmd=None):
        if cmd_key in self._cmd_keys:
            handler = self._cmd_keys[cmd_key]
            return handler()

        if str_cmd_marker in self._cmd_strings:
            handler = self._cmd_strings[str_cmd_marker]
            return handler(cmd)

    def _quit(self):
        raise urwid.ExitMainLoop()

    def reset_autocomplete(self):
        self._autocomplete = None

    def _emit_error(self, error):
        urwid.emit_signal(self, self.SIGNAL_ERROR, self, error)

    def autocomplete(self, word, command=False, argument=False,
            command_name=None, direction='forward'):

        if self._autocomplete is None:
            if command is True:
                suggestions = [cmd[1] for cmd in self._colon_cmds]
                self._autocomplete = Autocomplete(suggestions, word)

            if argument is True:
                try:
                    suggestions = self.cmd_args_suggestions[command_name]
                except KeyError:
                    suggestions = []
                self._autocomplete = Autocomplete(suggestions, word)

            return self._autocomplete.suggestion(direction)

        return self._autocomplete.suggestion(direction)

class SearchCmdProcessor:
    def __init__(self, search_callback):
        self._last_keyword = None
        self._last_search_result = None
        self._max_search_pos = None
        self._search_callback = search_callback

    def search(self, keyword):
        if keyword is None or len(keyword) == 0:
            return
        self._last_keyword = keyword
        self._last_search_result = self._search_callback(keyword)
        if self._last_search_result is not None:
            self._max_search_pos = self._last_search_result[0]
            return
        self._emit_error(u'Nothing found')

    def search_next(self):
        if self._last_keyword is None:
            return
        if self._last_search_result is None:
            return
        index, row = self._last_search_result
        result = self._search_callback(self._last_keyword,
                pos=index + 1)
        if result is not None:
            self._last_search_result = result
            if self._last_search_result[0] > self._max_search_pos:
                self._max_search_pos = self._last_search_result[0]
        else:
            self._last_search_result = (0, self._last_search_result[1])
            return self.search_next()

    def search_prev(self):
        if self._last_keyword is None:
            return
        if self._last_search_result is None:
            return
        index, row = self._last_search_result
        result = self._search_callback(self._last_keyword,
                pos=index, reverse=True)
        if result is not None:
            self._last_search_result = result
            if self._last_search_result[0] > self._max_search_pos:
                self._max_search_pos = self._last_search_result[0]
        else:
            self._last_search_result = (self._max_search_pos + 1, self._last_search_result[1])
            return self.search_prev()

