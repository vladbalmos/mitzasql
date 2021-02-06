# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

class EmacsKeysMixin:
    def keypress(self, size, key):
        if key == 'ctrl e':
            return 'end'
        if key == 'ctrl a':
            return 'home'
        if key == 'ctrl h':
            return 'backspace'
        if key == 'ctrl w':
            self._remove_word(direction='back')
            return
        if key == 'meta d':
            self._remove_word(direction='forward')
            return
        if key == 'meta b':
            self._move_to_word(direction='back')
            return
        if key == 'meta f':
            self._move_to_word(direction='forward')
            return
        if key == 'ctrl f':
            self.edit_pos += 1
            return
        if key == 'ctrl b':
            if self.edit_pos != 0:
                self.edit_pos -= 1
            return
        return key

    def _remove_word(self, direction):
        '''Remove word until first separator character (back or forward)'''
        old_pos = self.edit_pos
        self._move_to_word(direction)
        new_pos = self.edit_pos
        if direction == 'back':
            self.edit_text = self.edit_text[0:new_pos] + self.edit_text[old_pos:]
            self.edit_pos = new_pos
        else:
            self.edit_text = self.edit_text[0:old_pos] + self.edit_text[new_pos:]
            self.edit_pos = old_pos


    def _move_to_word(self, direction):
        if direction == 'back':
            if self.edit_pos == 0:
                return
            text = self.edit_text[0:self.edit_pos-1]
            pos = self.edit_pos - 1
            found_alnum = False
            for char in reversed(text):
                pos -= 1
                if char.isalnum():
                    self.edit_pos = pos
                    found_alnum = True
                    continue
                if found_alnum:
                    return

            if not found_alnum:
                self.edit_pos = 0
            return

        if self.edit_pos == len(self.edit_text):
            return

        text = self.edit_text[self.edit_pos+1:]
        pos = self.edit_pos
        found_sep = False
        for char in text:
            pos += 1
            if not char.isalnum():
                self.edit_pos = pos
                found_sep = True
            elif found_sep is True:
                return

        if not found_sep:
            self.edit_pos = len(self.edit_text)
