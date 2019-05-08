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

"""urwid palette settings"""
default_theme = [
        ('error_message', 'white', 'dark red'),
        ('warning_message', 'black', 'brown'),
        ('info_message', 'white', 'dark blue', '', 'h186', 'g20'),

        ('action_bar', 'black', 'light gray', '', 'h250', 'g20'),
        ('action_bar:action', 'white', 'dark blue', '', 'g80', 'g30'),
        ('action_bar:action_key', 'light red,bold', 'dark blue', '', 'h122,bold', 'g30'),
        # ('action_bar:content', 'light gray', '', '', 'light gray', ''),
        ('action_bar:content', '', '', '', '', ''),

        ('linebox', '', '', '', 'h186', ''),

        ('session_header', 'light red', '', '', 'h186,bold', 'g20'),

        ('command_bar', 'white', 'dark blue', '', 'h117', 'g20'),

        ('list:item:unfocused', '', '', 'standout'),
        ('list:item:focused', 'black', 'light gray', 'standout'),

        ('editbox', 'white', 'dark blue', '', 'g20,bold', 'h144'),
        ('editbox:label', '', ''),

        ('theader', 'light cyan', ''),
        ('theader_sep', 'dark cyan', ''),

        ('trow_focused', 'black', 'light gray'),
        ('tcell_more', 'light red', ''),

        ('tcell_null_unfocused', 'dark red', ''),
        ('tcell_null_focused', 'dark red', 'light gray'),

        ('tfooter', 'light red', '', '', 'h186', 'g10')

        ]

themes = {
        'default': default_theme
        }

def get_palette(name = 'default'):
    return themes[name]

