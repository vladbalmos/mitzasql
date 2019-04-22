import urwid

from mitzasql.ui import main_loop as shared_main_loop
from mitzasql.ui.widgets.error_dialog import ErrorDialog
from mitzasql.ui.widgets.quit_dialog import QuitDialog

class SessionPopupLauncher(urwid.PopUpLauncher):
    def __init__(self, widget):
        super().__init__(widget)
        self._max_width = None
        self._max_height = None
        self._suggested_width = None
        self._suggested_heigth = None
        self.showing_error_modal = False

        self._popup_factory_method = None

    def create_pop_up(self):
        return self._popup_factory_method()

    def get_pop_up_parameters(self):
        if self._suggested_width is not None:
            width = self._suggested_width
        else:
            width = int(60 * self._max_width / 100)

        if self._suggested_heigth is not None:
            height = self._suggested_heigth
        else:
            height = int(30 * self._max_height / 100)

        left = (self._max_width - width) / 2
        top = (self._max_height - height) / 2

        return {'left': left, 'top': top, 'overlay_width': width, 'overlay_height':
                height}

    def close_pop_up(self, *args, **kwargs):
        self.showing_error_modal = False
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
        self._suggested_heigth = 5
        self._suggested_width = 40
        def factory_method():
            dialog = urwid.Text(u'\nLoading...', align='center')
            dialog = urwid.Filler(dialog)
            dialog = urwid.AttrMap(urwid.LineBox(dialog), 'linebox')
            return dialog
        self._popup_factory_method = factory_method
        result = self.open_pop_up()
        shared_main_loop.refresh()
        self._suggested_heigth = None
        self._suggested_width = None
        return result


    def render(self, size, focus=False):
        self._max_width, self._max_height = size
        return super().render(size, focus)

