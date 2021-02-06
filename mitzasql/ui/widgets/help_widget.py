# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import os
import urwid

from .info_widget import InfoWidget

class HelpWidget(InfoWidget):

    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), 'help.txt')
        try:
            with open(path) as file:
                help = file.read()
        except:
            help = u'Error: Unable to open help file'
        contents = [urwid.AttrMap(urwid.Text(help), 'default'),
                # Empty line is required, or else the 'end' key won't work
                urwid.AttrMap(urwid.Text(''), 'default')]
        super().__init__(contents)

    @property
    def name(self):
        return u'Help'
