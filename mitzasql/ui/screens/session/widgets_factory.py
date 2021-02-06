# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

from mitzasql.db.model import (DatabasesModel, DBTablesModel, TableModel, QueryModel)

from ..base_widgets_factory import BaseWidgetsFactory
from ...widgets.db_view import DBView
from ...widgets.db_tables_view import DBTablesView
from ...widgets.table_view import TableView
from ...widgets.query_view import QueryView

class WidgetsFactory(BaseWidgetsFactory):

    def _get_factory_methods(self):
        factory_methods = {}
        factory_methods['databases_view'] = self.create_databases_view
        factory_methods['db_tables_view'] = self.create_db_tables_view
        factory_methods['table_view'] = self.create_table_view
        factory_methods['query_view'] = self.create_query_view

        return factory_methods

    def create_databases_view(self, connection):
        model = DatabasesModel(connection)
        view = DBView(model, connection)
        self._connect_signal(view, view.SIGNAL_ACTION_QUIT,
                self.change_fsm_state, user_args=['quit'])
        self._connect_signal(view, view.SIGNAL_ACTION_SELECT_DB,
                self.change_fsm_state, user_args=['select'])
        self._connect_signal(view, view.SIGNAL_ACTION_RUN_QUERY,
                self.change_fsm_state, user_args=['run_query'])
        return view

    def create_db_tables_view(self, database, connection):
        model = DBTablesModel(connection, database)
        view = DBTablesView(model, connection)
        self._connect_signal(view, view.SIGNAL_ACTION_QUIT,
                self.change_fsm_state, user_args=['quit'])
        self._connect_signal(view, view.SIGNAL_ACTION_EXIT,
                self.change_fsm_state, user_args=['back'])
        self._connect_signal(view, view.SIGNAL_ACTION_RUN_QUERY,
                self.change_fsm_state, user_args=['run_query'])
        return view

    def create_table_view(self, table, connection):
        model = TableModel(connection, table)
        view = TableView(model, connection)
        self._connect_signal(view, view.SIGNAL_ACTION_QUIT,
                self.change_fsm_state, user_args=['quit'])
        self._connect_signal(view, view.SIGNAL_ACTION_EXIT,
                self.change_fsm_state, user_args=['back'])
        self._connect_signal(view, view.SIGNAL_ACTION_RUN_QUERY,
                self.change_fsm_state, user_args=['run_query'])
        return view

    def create_query_view(self, query, connection):
        model = QueryModel(connection, query)
        view = QueryView(model, connection)
        self._connect_signal(view, view.SIGNAL_ACTION_QUIT,
                self.change_fsm_state, user_args=['quit'])
        self._connect_signal(view, view.SIGNAL_ACTION_EXIT,
                self.change_fsm_state, user_args=['back'])
        self._connect_signal(view, view.SIGNAL_ACTION_RUN_QUERY,
                self.change_fsm_state, user_args=['run_query'])
        return view
