from collections import OrderedDict

import urwid
import mysql.connector.errors as errors

import mitzasql.db.schema as schema

MAX_ROWS_FOR_COLUMN_LENGTH_DETECTION = 100

class Model:
    SIGNAL_PRE_LOAD = 'preload'
    SIGNAL_LOAD = 'load'
    SIGNAL_NEW_DATA = 'new_data'

    SIGNALS = [SIGNAL_PRE_LOAD, SIGNAL_NEW_DATA, SIGNAL_LOAD]

    ''' Base model '''
    def __init__(self, data = [], columns = {}):
        self.data = data
        self.columns = columns
        self.rowcount = len(data)
        urwid.register_signal(self.__class__, self.SIGNALS)

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return self.rowcount

    def __iter__(self):
        for row in self.data:
            yield row

    def col_index(self, name):
        for index, item in enumerate(self.columns):
            if item['name'].lower() == name.lower():
                return index
        raise IndexError()

    def search(self, keyword, col_index, pos=0, reverse=False):
        if reverse is True:
            row_index = 1
            start = 0
            end = pos
        else:
            row_index = 0
            start = pos
            end = None

        data = self.data[start:end]

        if reverse is True:
            data = reversed(data)

        for row in data:
            col = row[col_index]
            if str(keyword).lower() in str(col).lower():
                if not reverse:
                    return (start + row_index, row)
                return (end - row_index, row)

            row_index += 1

class MysqlModel(Model):
    SIGNAL_ERROR = 'error'

    '''Base mysql query model'''
    def __init__(self, connection):
        self._con = connection
        self.last_error = None
        self.SIGNALS.extend([self.SIGNAL_ERROR])
        super().__init__()
        self._fetch_data()

    def _fetch_data(self):
        cursor = self._query_db()
        if cursor is None:
            self.data = []
            self.columns = []
            self.rowcount = 0
            return False
        self.data = cursor.fetchall()
        self.columns = self._schema(cursor).columns
        self.rowcount = cursor.rowcount
        return True

    def _schema(self, cursor):
        return schema.QuerySchema(cursor,
                self.data[0:MAX_ROWS_FOR_COLUMN_LENGTH_DETECTION])

    def reload(self):
        urwid.emit_signal(self, self.SIGNAL_PRE_LOAD, self)
        self._fetch_data()
        urwid.emit_signal(self, self.SIGNAL_LOAD, self)

    def execute_query(self, query, params=None):
        try:
            cursor = self._con.query(query, params)
            self.last_error = None
            return cursor
        except errors.Error as e:
            self.last_error = e
            urwid.emit_signal(self, self.SIGNAL_ERROR, self, e)

    def _query_db(self):
        '''Creates and executes a query cursor. Must be implemented by child
        models
        '''
        raise RuntimeError("Child model must implement this method")

class DatabasesModel(MysqlModel):
    '''Model for the 'SHOW DATABASES' query'''
    def __init__(self, connection):
        super().__init__(connection)

    def _query_db(self):
        query = 'SHOW DATABASES'
        cursor = self.execute_query(query)
        return cursor

class DBTablesModel(MysqlModel):
    '''Model for all the tables in the current database'''
    def __init__(self, connection, database):
        self.database = database
        super().__init__(connection)

    def _query_db(self):
        try:
            self._con.change_db(self.database)
        except errors.Error as e:
            self.last_error = e
            urwid.emit_signal(self, self.SIGNAL_ERROR, self, e)
            return

        # TODO: show view & procedure status
        query = 'SHOW TABLE STATUS FROM `{0}`'.format(self.database)
        cursor = self.execute_query(query)
        return cursor

class TableModel(MysqlModel):
    PAGINATION_LIMIT = 100

    '''Model for a database table/view'''
    def __init__(self, connection, table_name):
        self.table_name = table_name
        self.schema_error = None

        try:
            self._table_schema = schema.TableSchema(connection, table_name)
        except errors.Error as e:
            self.schema_error = e
            self.last_error = e

        self._limit = self.PAGINATION_LIMIT
        self._page = 1
        self._offset = 0
        self._column_order = None
        self._order_dir = None
        super().__init__(connection)

        self.loaded_rowcount = len(self.data)
        self.rowcount = self._count_rows()

    def _fetch_data(self):
        result = super()._fetch_data()
        return result

    def reload(self, reset_limit=True, reset_order=True):
        urwid.emit_signal(self, self.SIGNAL_PRE_LOAD, self)

        try:
            self._table_schema = schema.TableSchema(self._con, self.table_name)
            self.schema_error = None
            self.last_error = None
        except errors.Error as e:
            self.schema_error = e
            self.last_error = e
            urwid.emit_signal(self, self.SIGNAL_LOAD, self)
            return

        if reset_limit:
            self._page = 1
            self._offset = 0

        if reset_order:
            self._column_order = None
            self._order_dir = None

        if self._fetch_data() is False:
            self.loaded_rowcount = 0
            self.rowcount = 0
            urwid.emit_signal(self, self.SIGNAL_LOAD, self)
            return

        self.loaded_rowcount = len(self.data)
        self.rowcount = self._count_rows()
        urwid.emit_signal(self, self.SIGNAL_LOAD, self)

    def _schema(self, cursor):
        self._table_schema.data = self.data[0:MAX_ROWS_FOR_COLUMN_LENGTH_DETECTION]
        self._table_schema.cursor = cursor
        return self._table_schema

    def _count_rows(self):
        query = 'SELECT COUNT(*) AS total FROM {0}'.format(self.table_name)
        cursor = self.execute_query(query)
        if cursor is None:
            return 0
        data = cursor.fetchall()
        return data[0][0]

    def load_next_set(self):
        self._increment_page()

        urwid.emit_signal(self, self.SIGNAL_PRE_LOAD, self)
        result = self._fetch_more_rows()
        if result is None:
            self._increment_page(-1)
            data = []
            data_length = 0
        else:
            data, data_length = result
        urwid.emit_signal(self, self.SIGNAL_NEW_DATA, self, data, data_length)

    def sort(self, column, direction):
        self._column_order = column
        self._order_dir = direction
        self._page = 1
        self._offset = 0

        self.reload(reset_limit=False, reset_order=False)

    def load_more(self, count):
        offset = self.loaded_rowcount
        limit = count + 100 # Load 100 more rows in advance

        old_limit = self._limit
        old_offset = self._offset

        self._limit = limit
        self._offset = offset

        urwid.emit_signal(self, self.SIGNAL_PRE_LOAD, self)
        result = self._fetch_more_rows()
        if result is None:
            self._limit = old_limit
            self._offset = old_offset
            data = []
            data_length = 0
        else:
            data, data_length = result
        urwid.emit_signal(self, self.SIGNAL_NEW_DATA, self, data, data_length)

        self._page = self.loaded_rowcount // self.PAGINATION_LIMIT
        self._limit = self.PAGINATION_LIMIT

    def _fetch_more_rows(self):
        cursor = self._query_db()
        if cursor is None:
            return None
        data = cursor.fetchall()
        data_length = len(data)
        self.data.extend(data)
        self.loaded_rowcount += data_length
        return (data, data_length)

    def _increment_page(self, value=1):
        self._page += value
        self._offset = (self._page - value) * self._limit

    def _query_db(self):
        if self.schema_error is not None:
            return
        select_columns = []
        for column, info in self._table_schema:
            if self._table_schema.column_is_text(info['type']) and info['max_len'] is not None and info['max_len'] > 256:
                column = 'LEFT(`{0}`, 256) as {1}'.format(column, column)
            elif self._table_schema.column_is_spatial(info['type']):
                column = 'ST_AsText(`{0}`) as {1}'.format(column, column)
            else:
                column = '`{0}`'.format(column)
            select_columns.append(column)

        query = 'SELECT {0} FROM `{1}`'.format(','.join(select_columns),
                self.table_name)

        if self._column_order is not None and self._order_dir is not None:
            query += ' ORDER BY `{0}` {1}'.format(self._column_order, self._order_dir)

        query += ' LIMIT {0:d}, {1:d}'.format(self._offset, self._limit)
        cursor = self.execute_query(query)
        return cursor

class QueryModel(MysqlModel):
    def __init__(self, connection, query):
        self.query = query
        super().__init__(connection)

    def _query_db(self):
        cursor = self.execute_query(self.query)
        return cursor

    def _fetch_data(self):
        cursor = self._query_db()
        if cursor is None or cursor.with_rows is False:
            self.data = []
            self.columns = []
            self.rowcount = 0
            return cursor is not None

        if cursor.with_rows:
            self.data = cursor.fetchall()
            self.columns = self._schema(cursor).columns
            self.rowcount = cursor.rowcount
        return True

