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

from mitzasql.ui.screens.session_select.session_select import SessionSelect
from mitzasql.ui.screens.session.session import Session
import mitzasql.constants as const

class Builder:
    """Screens builder

    Build UI screens and attaches their view to the top most widget.
    UI screens act like controllers for their child widgets and can interact
    directly with the main application instance.
    """

    def __init__(self, top_most_widget):
        self._top_most_widget = top_most_widget

        self._build_callbacks = {
                const.SCREEN_SESSION_SELECT: self._build_session_select,
                const.SCREEN_SESSION: self._build_session
                }

    def _build_session_select(self, sessions_registry):
        screen = SessionSelect(sessions_registry)
        return screen

    def _build_session(self, connection):
        screen = Session(connection)
        return screen

    def build_screen(self, name, display=False, **kwargs):
        build_callback = self._build_callbacks[name]
        screen = build_callback(**kwargs)
        if display is True:
            self._top_most_widget.original_widget = screen.view
        return screen

