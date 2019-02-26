import urwid

class Screen:
    """Base class for UI screens"""
    def __init__(self, signals=[]):
        self.focused_widget = None
        self.view = urwid.WidgetPlaceholder(urwid.SolidFill(' '))
        urwid.register_signal(self.__class__, signals)

    def quit(self, *args, **kwargs):
        raise urwid.ExitMainLoop()
