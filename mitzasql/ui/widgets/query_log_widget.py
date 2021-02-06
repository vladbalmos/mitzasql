# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file


import urwid

from .info_widget import InfoWidget

class QueryLogWidget(InfoWidget):
    def __init__(self, connection):
        contents = self._create_log(connection.QUERY_LOG)
        super().__init__(contents)
        self.focus_position = len(connection.QUERY_LOG) * 2

    @property
    def name(self):
        return u'Query Log'

    def _create_log(self, log):
        contents = []
        for entry in log:
            date, query, params, duration = entry
            date = date.strftime('%a %H:%M:%S')
            duration = '{:.3f}'.format(duration)
            log_entry = '{0}: {1}\nParams: {2}\nDuration: {3}s'.format(date,
                    query, params, duration)

            contents.append(urwid.AttrMap(urwid.Text(log_entry), 'default'))
            contents.append(urwid.Divider('-'))

        contents.append(urwid.Text(''))
        return contents
