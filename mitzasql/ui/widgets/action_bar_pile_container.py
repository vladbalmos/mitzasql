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

from .action_bar import ActionBar

class ActionBarPileContainer(urwid.WidgetPlaceholder):
    """Container widget which wraps another widget in a Pile, togheter with a
    status and an action bar

    If a key associated with an action is pressed, the widget emits the corresponding action
    signal.
    """
    SIGNAL_ACTION = 'action'
    SIGNALS = [SIGNAL_ACTION]

    def __init__(self, body, actions, height=None, line_box=False, line_box_title=''):
        self._actions = []
        self._actions_to_signals = {}
        self._body = body
        self._status_bar = urwid.Text('')
        self._prepare_actions_and_signals(actions)
        self._action_bar = urwid.AttrMap(ActionBar(self._actions), 'action_bar')
        self._container = self._make_container(height=height)

        if line_box is True:
            self._container = urwid.LineBox(self._container,
                    title=line_box_title)

        super().__init__(urwid.AttrMap(self._container, 'linebox'))
        self._register_signals()

    def _make_container(self, height=None):
        if height is not None:
            body = (height, urwid.Filler(self._body))
        else:
            body = self._body

        container = urwid.Pile([self._body, ('weight', 1, self._status_bar), ('weight', 1, self._action_bar)])
        container = urwid.AttrMap(container, 'action_bar:content')
        return container

    def set_status_message(self, message, error=False, warning=False):
        if error is False and warning is False:
            attribute = 'info_message'
        elif error is True:
            attribute = 'error_message'
        elif warning is True:
            attribute = 'warning_message'

        self._status_bar.set_text((attribute, message))

    def clear_status_message(self):
        self._status_bar.set_text('')

    def _register_signals(self):
        signals = self.SIGNALS
        if len(self._actions_to_signals):
            signals.extend(self._actions_to_signals.values())
        urwid.register_signal(self.__class__, signals)

    def _prepare_actions_and_signals(self, actions):
        _actions = []
        actions_to_signals = {}
        for action in actions:
            if len(action) == 3:
                key, action, signal = action
            else:
                key, action = action
                signal = None

            _actions.append((key, action))

            if signal is not None:
                actions_to_signals[key] = signal

        self._actions = _actions
        self._actions_to_signals = actions_to_signals

    def selectable(self):
        """This is required in order to catch user input"""
        return True

    def keypress(self, size, key):
        # Pass the keypress to the body widget
        if self._body.selectable() is True and self._body.keypress(size, key) is None:
            return
        # Check if any of the unhandled keys are registered with any actions
        # and trigger any corresponding signals
        for action_key, action_name in self._actions:
            if action_key.lower() == key.lower():
                urwid.emit_signal(self, self.SIGNAL_ACTION, self, action_name)

                if action_key in self._actions_to_signals:
                    signal = self._actions_to_signals[action_key]
                    urwid.emit_signal(self, signal, self, action_name)
                return
        return key

