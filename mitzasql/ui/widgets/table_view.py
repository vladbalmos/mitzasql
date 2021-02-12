# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

from collections import deque
import urwid
from .base_db_view import BaseDBView
from .mysql_table import MysqlTable
from ...table_filter_parser import Parser
from ...logger import logger

from mitzasql.ui.widgets.cmd_proc import (BaseCmdProcessor, CommandError)

class CommandProcessor(BaseCmdProcessor):
    def __init__(self, table_view):
        self._table_view = table_view
        BaseCmdProcessor.__init__(self)

        self._colon_cmds.extend([
                ('r', 'resize', self._resize_table),
                ('s', 'sort', self._sort_table),
                ('e', 'eq', self._filter_table('eq')),
                ('ne', 'neq', self._filter_table('neq')),
                ('lt', 'lt', self._filter_table('lt')),
                ('lte', 'lte', self._filter_table('lte')),
                ('gt', 'gt', self._filter_table('gt')),
                ('gte', 'gte', self._filter_table('gte')),
                ('in', 'in', self._filter_table('in')),
                ('nin', 'nin', self._filter_table('nin')),
                ('bt', 'between', self._filter_table('between')),
                ('nbt', 'nbetween', self._filter_table('nbetween')),
                ('n', 'null', self._filter_table('null')),
                ('nn', 'nnull', self._filter_table('nnull')),
                ('empty', 'empty', self._filter_table('empty')),
                ('nempty', 'nempty', self._filter_table('nempty')),
                ('k', 'like', self._filter_table('like')),
                ('nk', 'nlike', self._filter_table('nlike')),
                ('cf', 'clearfilters', self._filter_table('clearfilters'))
                ])

        self._cmd_strings = {
                ':': self.colon_handler
                }

    def _resize_table(self, *args):
        if not len(args):
            return
        if len(args) == 1:
            column = args[0]
            value = 1
        else:
            column, *value = args
            value = ' '.join(value)
        try:
            self._table_view.resize_tbl_col(column, value)
        except CommandError as e:
            self._emit_error(str(e))

    def _filter_table(self, op):
        def callback(*args):
            try:
                self._table_view.filter(op, *args)
            except CommandError as e:
                self._emit_error(str(e))
        return callback

    def _sort_table(self, *args):
        if not len(args):
            return

        if len(args) == 1:
            column = args[0]
            direction = 'asc'
        else:
            column, *direction = args
            direction = ' '.join(direction)
        try:
            self._table_view.sort(column, direction)
        except CommandError as e:
            self._emit_error(str(e))

class TableView(BaseDBView):
    SIGNAL_ACTION_SELECT_ROW = 'select_row'
    SIGNAL_ACTION_INFO = 'info'
    SIGNAL_ACTION_CHANGE_TABLE = 'change_table'

    def __init__(self, model, connection):
        self._command_processor = CommandProcessor(self)
        self._table_widget_cls = MysqlTable
        actions = [
                ('F3', u'F3 Info', self.SIGNAL_ACTION_INFO)
                ]
        super().__init__(model, connection, actions)
        self._set_cmd_args_suggestions()
        self.SIGNALS.extend([self.SIGNAL_ACTION_SELECT_ROW,
            self.SIGNAL_ACTION_INFO, self.SIGNAL_ACTION_CHANGE_TABLE])
        self._connect_table_signals()

    def refresh(self, table, connection, **kwargs):
        if table == self._model.table_name and self._model.database == connection.database:
            if 'force_refresh' in kwargs and kwargs['force_refresh'] == True or self._model.last_error:
                self._model.reload()
            return

        self._model.database = connection.database
        self._model.table_name = table
        self._model.reload()
        self._set_cmd_args_suggestions()
        self._update_breadcrumbs()

    def refresh_model(self, emitter, action):
        self._model.reload(reset_limit=False, reset_order=False, reset_where=False)

    def _set_cmd_args_suggestions(self):
        cmd_args_suggestions = [c['name'] for c in self._model.columns]
        self._command_processor.cmd_args_suggestions['eq'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['neq'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['lt'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['lte'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['gt'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['gte'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['in'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['nin'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['between'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['nbetween'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['null'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['nnull'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['empty'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['nempty'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['like'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['nlike'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['resize'] = cmd_args_suggestions
        self._command_processor.cmd_args_suggestions['sort'] = self._command_processor.cmd_args_suggestions['resize']


    def __del__(self):
        self._disconnect_table_signals()
        super().__del__()

    def _connect_table_signals(self):
        urwid.connect_signal(self._table, self._table.SIGNAL_ROW_SELECTED,
                self.select_row)

    def _disconnect_table_signals(self):
        urwid.disconnect_signal(self._table, self._table.SIGNAL_ROW_SELECTED,
                self.select_row)

    def select_row(self, emitter, row):
        urwid.emit_signal(self, self.SIGNAL_ACTION_SELECT_ROW, self, row)

    @property
    def table(self):
        return self._model.table_name

    def resize_tbl_col(self, column, value=1):
        try:
            value = int(value)
            col_index = self._model.col_index(column.lower())
        except IndexError as e:
            raise CommandError(u'Column not found!')
        except ValueError as e:
            raise CommandError(u'Invalid column width!')
        self._table.resize_col(col_index, value)

    def sort(self, column, direction):
        if column not in [c['name'] for c in self._model.columns]:
            raise CommandError(u'Column not found!')

        if direction.lower() != 'asc' and direction.lower() != 'desc':
            raise CommandError(u'Invalid sort direction!')

        self._model.sort(column, direction)

    def filter(self, op, *args):
        if op == 'clearfilters':
            self._model.filter(None)
            return

        if not len(args):
            raise CommandError(u'Filter requires column!')

        arguments = deque(args)
        column = arguments.popleft()

        if column not in [c['name'] for c in self._model.columns]:
            raise CommandError(u'Column not found!')

        filters_without_values = ['null', 'nnull', 'empty', 'nempty']
        if not op in filters_without_values:
            filter_val = ' '.join(arguments)
            if not len(filter_val):
                raise CommandError("Filter requires value")

        if op == 'null':
            where = '`{0}` IS NULL'.format(column)
        elif op == 'nnull':
            where = '`{0}` IS NOT NULL'.format(column)
        elif op == 'empty':
            where = '`{0}` = \'\''.format(column)
        elif op == 'nempty':
            where = '`{0}` != \'\''.format(column)
        elif op == 'eq':
            where = '`{0}` = {1}'.format(column, self._escape_filter_value(filter_val, column))
        elif op == 'neq':
            where = '`{0}` != {1}'.format(column, self._escape_filter_value(filter_val, column))
        elif op == 'lt':
            where = '`{0}` < {1}'.format(column, self._escape_filter_value(filter_val, column))
        elif op == 'lte':
            where = '`{0}` <= {1}'.format(column, self._escape_filter_value(filter_val, column))
        elif op == 'gt':
            where = '`{0}` > {1}'.format(column, self._escape_filter_value(filter_val, column))
        elif op == 'gte':
            where = '`{0}` >= {1}'.format(column, self._escape_filter_value(filter_val, column))
        elif op == 'like':
            where = '`{0}` LIKE "{1}"'.format(column, filter_val)
        elif op == 'nlike':
            where = '`{0}` NOT LIKE "{1}"'.format(column, filter_val)
        elif op == 'in':
            values = ','.join(map(str.strip, filter_val.split(',')))
            if not len(values):
                raise CommandError("Filter requires value")
            where = '`{0}` IN ({1})'.format(column, values)
        elif op == 'nin':
            values = ','.join(map(str.strip, filter_val.split(',')))
            if not len(values):
                raise CommandError("Filter requires value")
            where = '`{0}` NOT IN ({1})'.format(column, values)
        elif op == 'between':
            p = Parser(filter_val)
            values = p.parse()
            if len(values) != 2:
                raise CommandError("Filter requires 2 values")

            values = list(map(lambda v: v.replace("'", "\\'"), values))
            where = "`{0}` BETWEEN '{1}' AND '{2}'".format(column, values[0], values[1])
        elif op == 'nbetween':
            p = Parser(filter_val)
            values = p.parse()
            if len(values) != 2:
                raise CommandError("Filter requires 2 values")
            values = list(map(lambda v: v.replace("'", "\\'"), values))
            where = "`{0}` NOT BETWEEN '{1}' AND '{2}'".format(column, values[0], values[1])

        self._model.filter(where)
        if self._model.last_error:
            self._model.clear_filter()

    def _escape_filter_value(self, value, column):
        for c in self._model.columns:
            if column != c['name']:
                continue

            if c['is_text'] or c['is_temporal']:
                value = value.replace("'", "\\'")
                logger.info(value)
                return "'{0}'".format(value)

            return value;

        return value

    def keypress(self, size, key):
        if key == 'ctrl o':
            urwid.emit_signal(self, self.SIGNAL_ACTION_CHANGE_TABLE, self)
            return
        return super().keypress(size, key)
