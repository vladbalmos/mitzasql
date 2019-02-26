import urwid

from mitzasql.ui import main_loop as shared_main_loop
from mitzasql.state_machine import StateMachine
from mitzasql.db.connection import Connection
from mitzasql.db.model import (DatabasesModel, DBTablesModel, TableModel)
from mitzasql.ui.screens.screen import Screen
from mitzasql.ui.widgets.db_view import DBView
from mitzasql.ui.widgets.db_tables_view import DBTablesView
from mitzasql.ui.widgets.table_view import TableView
from mitzasql.ui.widgets.query_view import QueryView
from mitzasql.ui.widgets.error_dialog import ErrorDialog
from mitzasql.ui.widgets.quit_dialog import QuitDialog
from mitzasql.logger import logger
from .widgets_factory import WidgetsFactory
from . import states


class PopupLauncher(urwid.PopUpLauncher):
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

class Session(Screen):
    def __init__(self, connection):
        super().__init__()
        self.view = PopupLauncher(urwid.SolidFill(' '))
        self._connection = connection
        self._last_database = None
        self._last_table = None
        self._last_query = None
        self._last_primary_view = None
        self._state_machine = self._init_state_machine()
        self._state_machine.set_initial_state(states.STATE_INITIAL)
        self._widgets_factory = WidgetsFactory(self._state_machine)
        self._state_machine.run()

    def _init_state_machine(self):
        state_machine = StateMachine('session')
        state_machine.add_state(states.STATE_INITIAL, self.initial_state, {
            'database_selected': states.STATE_SHOW_DB_TABLES,
            'no_database_selected': states.STATE_SHOW_DATABASES
            })

        state_machine.add_state(states.STATE_SHOW_DATABASES, self.show_databases, {
            'select': states.STATE_SHOW_DB_TABLES,
            'quit': states.STATE_QUIT,
            'run_query': states.STATE_SHOW_QUERY_TABLE
            })

        state_machine.add_state(states.STATE_SHOW_DB_TABLES,
                self.show_db_tables, {
            'back': states.STATE_SHOW_DATABASES,
            'select': states.STATE_SHOW_TABLE,
            'quit': states.STATE_QUIT,
            'run_query': states.STATE_SHOW_QUERY_TABLE
            })

        state_machine.add_state(states.STATE_SHOW_TABLE, self.show_table, {
            'back': states.STATE_SHOW_DB_TABLES,
            'quit': states.STATE_QUIT,
            'run_query': states.STATE_SHOW_QUERY_TABLE
            })

        state_machine.add_state(states.STATE_SHOW_QUERY_TABLE, self.show_query_table, {
            'run_query': states.STATE_SHOW_QUERY_TABLE,
            'back': states.STATE_GOTO_PREV_VIEW,
            'quit': states.STATE_QUIT,
            })
        state_machine.add_state(states.STATE_GOTO_PREV_VIEW,
                self.goto_prev_view, {
                    'show_db_view': states.STATE_SHOW_DATABASES,
                    'show_db_tables_view': states.STATE_SHOW_DB_TABLES,
                    'show_table_view': states.STATE_SHOW_TABLE
                    })
        state_machine.add_state(states.STATE_QUIT, self.quit, {
            'back': states.STATE_GOTO_PREV_VIEW
            })
        return state_machine

    def quit(self, *args, **kwargs):
        def goto_previous_state(*args, **kwargs):
            self._state_machine.change_state('back')
        return self.view.show_quit_dialog(on_no=goto_previous_state)

    def initial_state(self):
        db_name = self._connection.database
        if db_name is None or len(db_name) == 0:
            self._state_machine.change_state('no_database_selected')
            return
        self._state_machine.change_state('database_selected', self, db_name)

    def show_databases(self, *args, **kwargs):
        self.focused_widget = self._widgets_factory.create('databases_view', self._connection)
        self.view.original_widget = self.focused_widget
        self._last_primary_view = self.focused_widget
        self.focused_widget.set_model_error_handler(self.handle_model_error)

    def show_db_tables(self, emitter, database=None):
        if database is None:
            database = self._last_database
        self._last_database = database
        self.focused_widget = self._widgets_factory.create('db_tables_view', database, self._connection)
        self.view.original_widget = self.focused_widget
        self._last_primary_view = self.focused_widget
        self.focused_widget.set_model_error_handler(self.handle_model_error)

    def show_table(self, emitter, table):
        self.focused_widget = self._widgets_factory.create('table_view', table, self._connection)
        self.view.original_widget = self.focused_widget
        self._last_primary_view = self.focused_widget
        self.focused_widget.set_model_error_handler(self.handle_model_error)

    def show_query_table(self, emitter, query):
        if not isinstance(emitter, QueryView):
            self.view.show_loading_dialog()
        self.focused_widget = self._widgets_factory.create('query_view', query, self._connection)
        self.view.original_widget = self.focused_widget
        if not isinstance(emitter, QueryView):
            self.view.close_pop_up()
        self.focused_widget.set_model_error_handler(self.handle_model_error)

    def goto_prev_view(self, *args, **kwargs):
        if isinstance(self._last_primary_view, DBView):
            self._state_machine.change_state('show_db_view', self)
            return

        if isinstance(self._last_primary_view, DBTablesView):
            self._state_machine.change_state('show_db_tables_view', self)
            return

        if isinstance(self._last_primary_view, TableView):
            self._state_machine.change_state('show_table_view', self,
                    self._last_primary_view.table)
            return

    def handle_model_error(self, emitter, model, error):
        if self._connection.is_fatal_error(error):
            return self.view.show_fatal_error(error)

        return self.view.show_error(error)
