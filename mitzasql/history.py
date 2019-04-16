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

class History:
    def __init__(self):
        self.history = []
        self.pos = -1

    def append(self, item):
        self.history.append(item)
        self.pos = len(self)

    def __len__(self):
        return len(self.history)

    @property
    def last(self):
        try:
            item = self.history[len(self) - 1]
        except IndexError:
            return
        return item

    @property
    def prev(self):
        try:
            if self.pos > 0:
                self.pos -= 1
            item = self.history[self.pos]
        except IndexError:
            return

        return item

    @property
    def next(self):
        try:
            if self.pos < (len(self) - 1):
                self.pos += 1
            item = self.history[self.pos]
        except IndexError:
            return
        return item
