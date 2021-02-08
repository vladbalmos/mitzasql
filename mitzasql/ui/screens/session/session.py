# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

from ....state_machine import StateMachine
from ....db.connection import Connection
from ....db.model import (DBTablesModel, TriggerModel, ProcedureModel, TableInfoModel, ViewInfoModel)
from ..screen import Screen
from ...widgets.db_view import DBView
from ...widgets.db_tables_view import DBTablesView
from ...widgets.table_view import TableView
from ...widgets.query_view import QueryView
from ...widgets.query_log_widget import QueryLogWidget
from ...widgets.session_popup_launcher import SessionPopupLauncher
from ...widgets.trigger_widget import TriggerWidget
from ...widgets.procedure_widget import ProcedureWidget
from ...widgets.row_widget import RowWidget
from ...widgets.view_info_widget import ViewInfoWidget
from ...widgets.table_info_widget import TableInfoWidget
from ...widgets.table_changer_widget import TableChangerWidget
from ...widgets.help_widget import HelpWidget
from .widgets_factory import WidgetsFactory
from . import states

def show_loading_decorator(method):
    def wrapper(self, *args, **kwargs):
        if not self.focused_widget:
            method(self, *args, **kwargs)

        prev_widget = self.focused_widget
        prev_widget.toggle_loading_status(True)
        method(self, *args, **kwargs)
        prev_widget.toggle_loading_status(False)
    return wrapper

class Session(Screen):
    def __init__(self, connection):
        super().__init__()
        self.view = SessionPopupLauncher(urwid.SolidFill(' '))
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

    @show_loading_decorator
    def show_databases(self, *args, **kwargs):
        self._connection.database = None
        self.focused_widget = self._widgets_factory.create('databases_view',
                self._connection, **kwargs)
        self._bind_help_handler(self.focused_widget)
        self._bind_log_handler(self.focused_widget)
        self.view.original_widget = self.focused_widget
        self._last_primary_view = self.focused_widget
        self.focused_widget.set_model_error_handler(self.handle_model_error)

    @show_loading_decorator
    def show_db_tables(self, emitter, database=None, **kwargs):
        if database is None:
            database = self._last_database
        self._last_database = database
        self.focused_widget = self._widgets_factory.create('db_tables_view',
                database, self._connection, **kwargs)
        self._bind_help_handler(self.focused_widget)
        self._bind_log_handler(self.focused_widget)
        self.view.original_widget = self.focused_widget
        self._last_primary_view = self.focused_widget
        self.focused_widget.set_model_error_handler(self.handle_model_error)

        if hasattr(self.focused_widget, 'select_handler_bound'):
            return

        non_table_types = ('PROCEDURE', 'TRIGGER', 'FUNCTION')
        def on_select(emitter, row):
            object_type = row[-1]
            if object_type not in non_table_types:
                self._state_machine.change_state('select', emitter, row[0])
                return

            if object_type == 'TRIGGER':
                model = TriggerModel(self._connection, self._connection.database, row[0])
                if model.last_error is not None:
                    self.view.show_error(model.last_error)
                    return
                widget = TriggerWidget(model)
                self.view.show_big_popup(widget)
                return

            if object_type == 'FUNCTION' or object_type == 'PROCEDURE':
                model = ProcedureModel(self._connection, self._connection.database, row[0])
                if model.last_error is not None:
                    self.view.show_error(model.last_error)
                    return
                widget = ProcedureWidget(model)
                self.view.show_big_popup(widget)
                return

        urwid.connect_signal(self.focused_widget, self.focused_widget.SIGNAL_ACTION_SELECT_TABLE, on_select)
        self.focused_widget.select_handler_bound = True

    @show_loading_decorator
    def show_table(self, emitter, table, **kwargs):
        self.focused_widget = self._widgets_factory.create('table_view', table, self._connection, **kwargs)
        self.view.original_widget = self.focused_widget
        self._bind_help_handler(self.focused_widget)
        self._bind_log_handler(self.focused_widget)
        self._last_primary_view = self.focused_widget
        self.focused_widget.set_model_error_handler(self.handle_model_error)

        if not hasattr(self.focused_widget, 'change_table_handler_bound'):
            def on_change_table(emitter):
                database = self._connection.database
                model = DBTablesModel(self._connection, database)
                if model.last_error is not None:
                    self.view.show_error(model.last_error)
                    return
                widget = TableChangerWidget(model)
                urwid.connect_signal(widget, widget.SIGNAL_CHANGE_TABLE,
                        self.switch_table)
                self.view.show_table_changer(widget)
                return

            urwid.connect_signal(self.focused_widget,
                    self.focused_widget.SIGNAL_ACTION_CHANGE_TABLE,
                    on_change_table)
            self.focused_widget.change_table_handler_bound = True


        if not hasattr(self.focused_widget, 'select_handler_bound'):
            def on_select(emitter, row):
                columns = self.focused_widget.model.columns
                widget = RowWidget(row, columns)
                self.view.show_big_popup(widget)
                return

            urwid.connect_signal(self.focused_widget,
                    self.focused_widget.SIGNAL_ACTION_SELECT_ROW, on_select)
            self.focused_widget.select_handler_bound = True

        if not hasattr(self.focused_widget, 'info_handler_bound'):
            def on_info(emitter, action):
                table_name = emitter.model.table_name

                result = TableInfoModel.is_view(self._connection,
                        self._connection.database, table_name)

                if result is not False:
                    viewInfoModel = result
                    if viewInfoModel.last_error is not None:
                        self.view.show_error(viewInfoModel.last_error)
                        return
                    widget = ViewInfoWidget(viewInfoModel)
                    self.view.show_big_popup(widget)
                    return
                else:
                    model = TableInfoModel(self._connection,
                            self._connection.database, table_name)
                    if model.last_error is not None:
                        self.view.show_error(model.last_error)
                        return
                    widget = TableInfoWidget(model)
                    self.view.show_big_popup(widget)
                    return

            urwid.connect_signal(self.focused_widget,
                    self.focused_widget.SIGNAL_ACTION_INFO, on_info)
            self.focused_widget.info_handler_bound = True

    def show_query_table(self, emitter, query):
        if not isinstance(emitter, QueryView):
            self.view.show_loading_dialog()

        self.focused_widget = self._widgets_factory.create('query_view', query,
                self._connection.fresh, cache=False)

        self._bind_help_handler(self.focused_widget)
        self._bind_log_handler(self.focused_widget)
        self.view.original_widget = self.focused_widget
        if not isinstance(emitter, QueryView):
            self.view.close_pop_up()
        self.focused_widget.set_model_error_handler(self.handle_model_error)

        # If query cursor did not return rows, show info message
        model = self.focused_widget.model
        if not model.last_error and not model.has_rows:
            def go_back():
                self._state_machine.change_state('back', emitter, force_refresh=True)

            self.view.show_info(u'Affected rows: {0}'.format(model.affected_rows), on_close=go_back)
            return

        if hasattr(self.focused_widget, 'select_handler_bound'):
            return

        def on_select(emitter, row):
            columns = self.focused_widget.model.columns
            widget = RowWidget(row, columns)
            self.view.show_big_popup(widget)
            return

        urwid.connect_signal(self.focused_widget,
                self.focused_widget.SIGNAL_ACTION_SELECT_ROW, on_select)
        self.focused_widget.select_handler_bound = True

    def goto_prev_view(self, *args, **kwargs):
        if isinstance(self._last_primary_view, DBView):
            self._state_machine.change_state('show_db_view', self, **kwargs)
            return

        if isinstance(self._last_primary_view, DBTablesView):
            self._state_machine.change_state('show_db_tables_view', self, **kwargs)
            return

        if isinstance(self._last_primary_view, TableView):
            self._state_machine.change_state('show_table_view', self,
                    self._last_primary_view.table, **kwargs)
            return

    def handle_model_error(self, emitter, model, error):
        if self._connection.is_fatal_error(error):
            return self.view.show_fatal_error(error)

        def go_back():
            if self._state_machine.get_current_state() == states.STATE_SHOW_DATABASES:
                raise urwid.ExitMainLoop()

            self._state_machine.change_state('back', emitter)

        return self.view.show_error(error, on_close=go_back)

    def switch_table(self, emitter, table):
        self.view.close_pop_up()
        self.show_table(emitter, table)

    def _bind_help_handler(self, view):
        if hasattr(view, 'help_handler_bound'):
            return

        def on_help(emitter, action):
            widget = HelpWidget()
            self.view.show_big_popup(widget)

        view.help_handler_bound = True
        urwid.connect_signal(view, view.SIGNAL_ACTION_HELP, on_help)

    def _bind_log_handler(self, view):
        if hasattr(view, 'log_handler_bound'):
            return

        def on_show_log(emitter, action):
            widget = QueryLogWidget(self._connection)
            self.view.show_big_popup(widget)

        view.log_handler_bound = True
        urwid.connect_signal(view, view.SIGNAL_ACTION_QUERY_LOG, on_show_log)

