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

from mitzasql.logger import LoggerMixin

class StateMachine(LoggerMixin):
    """Finite state machine implementation"""
    def __init__(self, name):
        self._name = name
        self._handlers = {}
        self._transition_table = {}
        self._current_state = None
        self.set_log_prefix('FSM')

    def add_state(self, name, handler, transition_table=None):
        self._handlers[name] = handler
        if transition_table is not None:
            self._transition_table[name] = transition_table

    def get_current_state(self):
        return self._current_state

    def set_initial_state(self, name):
        self._log('Setting initial state to "%s"', name)
        self._current_state = name

    def run(self, *args, **kwargs):
        self._log('Transitioning to state "%s" with args: %s, kwargs: %s',
                self._current_state, args, kwargs)
        try:
            handler = self._handlers[self._current_state]
        except KeyError as e:
            self.log_critical('No handler registered for state: %s',
                    self._current_state)
            raise e

        handler(*args, **kwargs)
        self._log('Current state is "%s"', self._current_state)

    def change_state(self, input, *args, **kwargs):
        self._log('Received input: %s', input)
        try:
            transition_table = self._transition_table[self._current_state]
            next_state = transition_table[input]
        except KeyError as e:
            self.log_critical('Next state is not defined for input: %s', input)
            raise e

        self._current_state = next_state
        self.run(*args, **kwargs)

    def _log(self, message, *args):
        message = '"{0}": {1}'.format(self._name, message)
        self.log_debug(message, *args)
