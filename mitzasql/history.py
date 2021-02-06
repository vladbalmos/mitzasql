# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

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
