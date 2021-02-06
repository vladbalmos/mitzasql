# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .. import constants as const
from .screens.session_select.session_select import SessionSelect
from .screens.session.session import Session

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

