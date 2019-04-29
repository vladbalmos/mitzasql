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

from mitzasql.ui import main_loop as shared_main_loop
from mitzasql.ui.widgets.error_dialog import ErrorDialog
from mitzasql.ui.widgets.info_dialog import InfoDialog
from mitzasql.ui.widgets.quit_dialog import QuitDialog

class SessionPopupLauncher(urwid.PopUpLauncher):
    DEFAULT_WR = 60
    DEFAULT_HR = 30
    def __init__(self, widget):
        super().__init__(widget)
        self._max_width = None
        self._max_height = None
        self._width_ratio = self.DEFAULT_WR
        self._height_ratio = self.DEFAULT_HR
        # Used in testing
        self.showing_error_modal = False

        self._popup_factory_method = None

    def create_pop_up(self):
        return self._popup_factory_method()

    def get_pop_up_parameters(self):
        width = int(self._width_ratio * self._max_width / 100)
        height = int(self._height_ratio * self._max_height / 100)

        left = (self._max_width - width) / 2
        top = (self._max_height - height) / 2

        return {'left': left, 'top': top, 'overlay_width': width, 'overlay_height':
                height}

    def close_pop_up(self, *args, **kwargs):
        self.showing_error_modal = False
        self._reset_popup_size_ratio()
        return super().close_pop_up()

    def quit(self, *args, **kwargs):
        raise urwid.ExitMainLoop()

    def show_fatal_error(self, error):
        self.showing_error_modal = True
        def factory_method():
            dialog = ErrorDialog(error, title=u'Unhandled Exception',
                prefix='An unhandled error occured. Exception details:')
            urwid.connect_signal(dialog, dialog.SIGNAL_OK, self.quit)
            return urwid.Filler(dialog)
        self._popup_factory_method = factory_method
        return self.open_pop_up()

    def show_error(self, error):
        self.showing_error_modal = True
        def factory_method():
            dialog = ErrorDialog(error)
            urwid.connect_signal(dialog, dialog.SIGNAL_OK, self.close_pop_up)
            return urwid.Filler(dialog)
        self._popup_factory_method = factory_method
        return self.open_pop_up()

    def show_info(self, message):
        def factory_method():
            dialog = InfoDialog(message)
            urwid.connect_signal(dialog, dialog.SIGNAL_OK, self.close_pop_up)
            return urwid.Filler(dialog)
        self._popup_factory_method = factory_method
        return self.open_pop_up()

    def close_pop_up_then(self, callback):
        '''Close popup then execute callback'''
        def fn(*args, **kwargs):
            self.close_pop_up()
            callback()
        return fn

    def show_quit_dialog(self, on_no):
        def factory_method():
            dialog = QuitDialog()
            urwid.connect_signal(dialog, dialog.SIGNAL_OK, self.quit)
            urwid.connect_signal(dialog, dialog.SIGNAL_CANCEL,
                    self.close_pop_up_then(on_no))
            return urwid.Filler(dialog)
        self._popup_factory_method = factory_method
        return self.open_pop_up()

    def show_loading_dialog(self):
        self._width_ratio = 40
        self._height_ratio = 30
        def factory_method():
            dialog = urwid.Text(u'\nLoading...', align='center')
            dialog = urwid.Filler(dialog)
            dialog = urwid.AttrMap(urwid.LineBox(dialog), 'linebox')
            return dialog
        self._popup_factory_method = factory_method
        result = self.open_pop_up()
        shared_main_loop.refresh()
        return result

    def show_big_popup(self, widget):
        self._width_ratio = 90
        self._height_ratio = 80
        def factory_method():
            dialog = urwid.AttrMap(urwid.LineBox(widget, title=widget.name), 'linebox')
            urwid.connect_signal(widget, widget.SIGNAL_ESCAPE, self.close_pop_up)
            return dialog
        self._popup_factory_method = factory_method
        result = self.open_pop_up()
        shared_main_loop.refresh()
        return result

    def show_table_changer(self, widget):
        self._width_ratio = 25
        self._height_ratio = 70
        def factory_method():
            dialog = urwid.AttrMap(urwid.LineBox(widget, title=u'Change table'), 'linebox')
            urwid.connect_signal(widget, widget.SIGNAL_ESCAPE, self.close_pop_up)
            return dialog
        self._popup_factory_method = factory_method
        result = self.open_pop_up()
        shared_main_loop.refresh()
        return result

    def _reset_popup_size_ratio(self):
        self._width_ratio = self.DEFAULT_WR
        self._height_ratio = self.DEFAULT_HR

    def render(self, size, focus=False):
        self._max_width, self._max_height = size
        return super().render(size, focus)
