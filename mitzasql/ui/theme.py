# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

"""urwid palette settings"""
default_theme = [
        ('error_message', 'white', 'dark red'),
        ('warning_message', 'black', 'brown'),
        ('info_message', 'white', 'dark blue', '', 'h186', 'g20'),

        ('action_bar', 'black', 'light gray', '', 'h250', 'g20'),
        ('action_bar:action', 'white', 'dark blue', '', 'g80', 'g30'),
        ('action_bar:action_key', 'light red,bold', 'dark blue', '', 'h122,bold', 'g30'),
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

        ('tfooter', 'light red', '', '', 'h186', 'g10'),

        # autocomplete
        ('suggestion:highlight', 'light red,bold', '', '', 'h122,bold', ''),
        ('suggestion', 'white', '', '', 'g80', ''),

        # sql syntax highlighting
        ('sql:default', '', ''),
        ('sql:keyword', 'dark cyan', '', '', 'h210,bold', ''),
        ('sql:function', 'dark cyan', '', '', 'h117', ''),
        ('sql:name', 'light gray', '', '', 'h186', ''),
        ('sql:punctuation', 'yellow', '', '', 'h122', ''),
        ('sql:number', 'dark green', '', '', 'h211', ''),
        ('sql:operator', '', ''),
        ('sql:string', 'light cyan', '', '', 'h202', ''),
        ('sql:keyword.type', 'dark cyan', '', '', 'h210', ''),
        ('sql:builtin', 'dark cyan', '', '', 'h186', '')

        ]

themes = {
        'default': default_theme
        }

def get_palette(name = 'default'):
    return themes[name]

