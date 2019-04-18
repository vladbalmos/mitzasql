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

from mitzasql.db.model import (DatabasesModel, DBTablesModel, TableModel, QueryModel)

from mitzasql.ui.screens.base_widgets_factory import BaseWidgetsFactory
from mitzasql.ui.widgets.db_view import DBView
from mitzasql.ui.widgets.db_tables_view import DBTablesView
from mitzasql.ui.widgets.table_view import TableView
from mitzasql.ui.widgets.query_view import QueryView

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
