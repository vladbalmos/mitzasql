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
