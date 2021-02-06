# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

class Screen:
    """Base class for UI screens"""
    def __init__(self, signals=[]):
        self.focused_widget = None
        self.view = urwid.WidgetPlaceholder(urwid.SolidFill(' '))
        urwid.register_signal(self.__class__, signals)

    def quit(self, *args, **kwargs):
        raise urwid.ExitMainLoop()
