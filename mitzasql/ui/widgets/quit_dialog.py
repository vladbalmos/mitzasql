import urwid

from .dialog import Dialog

class QuitDialog(Dialog):
    SIGNAL_CANCEL = 'cancel'

    def __init__(self):
        actions = [
            ('k', 'Ok', self.SIGNAL_OK),
            ('C', 'Cancel', self.SIGNAL_CANCEL),
            ]
        message = u'\nAre you sure you want to quit?'
        super().__init__(message, title=u'Quit', actions=actions)
