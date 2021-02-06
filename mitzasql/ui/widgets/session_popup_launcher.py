# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from .. import main_loop as shared_main_loop
from .error_dialog import ErrorDialog
from .info_dialog import InfoDialog
from .quit_dialog import QuitDialog

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

    def show_error(self, error, on_close=None):
        self.showing_error_modal = True

        def on_ok_signal(*args, **kwargs):
            self.close_pop_up()

            if callable(on_close):
                on_close()

        def factory_method():
            dialog = ErrorDialog(error)
            urwid.connect_signal(dialog, dialog.SIGNAL_OK,
                    on_ok_signal)
            return urwid.Filler(dialog)

        self._popup_factory_method = factory_method
        return self.open_pop_up()

    def show_info(self, message, on_close=None):

        def on_ok_signal(*args, **kwargs):
            self.close_pop_up()

            if callable(on_close):
                on_close()

        def factory_method():
            dialog = InfoDialog(message)
            urwid.connect_signal(dialog, dialog.SIGNAL_OK, on_ok_signal)
            return urwid.Filler(dialog)

        self._popup_factory_method = factory_method
        return self.open_pop_up()

    def close_pop_up_then(self, callback):
        '''Close popup then execute callback'''
        def fn(*args, **kwargs):
            self.close_pop_up()
            callback()
        return fn

    def show_quit_dialog(self, on_no=None):
        def factory_method():
            dialog = QuitDialog()
            urwid.connect_signal(dialog, dialog.SIGNAL_OK, self.quit)

            if on_no is not None:
                urwid.connect_signal(dialog, dialog.SIGNAL_CANCEL,
                        self.close_pop_up_then(on_no))
            else:
                urwid.connect_signal(dialog, dialog.SIGNAL_CANCEL,
                        self.close_pop_up)
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
            urwid.connect_signal(widget, widget.SIGNAL_QUIT,
                    self.close_pop_up_then(self.show_quit_dialog))
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
