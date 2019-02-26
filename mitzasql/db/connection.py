import time

import urwid
import mysql.connector
from mysql.connector import (errorcode, errors)

from mitzasql.logger import (LoggerMixin, logger)

class Connection(LoggerMixin):
    SIGNAL_EXCEPTION = 'exception'
    def __init__(self, connection_data, session_name=None):
        self.set_log_prefix('Connection')
        self.is_tcp = False
        self.database = None
        self._retry_count = 0
        self.query_log = []
        self.con = self._create_mysql_connection(connection_data)
        self._connection_data = connection_data
        try:
            self.session_name = connection_data['name']
        except KeyError:
            self.session_name = session_name
        urwid.register_signal(self.__class__, [self.SIGNAL_EXCEPTION])

    def _create_mysql_connection(self, connection_data):
        kwargs = {
                'user': connection_data['username'],
                'password': connection_data['password'],
                'connection_timeout': 5,
                'autocommit': True,
                'use_pure': True
                }

        protocol, host = self._extract_host(connection_data['host'])
        if protocol == 'tcp':
            kwargs['host'] = host
            kwargs['port'] = connection_data['port']
            self.is_tcp = True
        else:
            kwargs['unix_socket'] = host

        if 'database' in connection_data and len(connection_data['database']) > 0:
            kwargs['database'] = connection_data['database']
            self.database = connection_data['database']

        kwargs['get_warnings'] = True

        con = mysql.connector.connect(**kwargs)
        self._retry_count = 0
        return con

    def _retry_connection(self):
        self.log_info("Disconnected. Retrying mysql connection...")
        if self._retry_count >= 5:
            return False

        try:
            self.con = self._create_mysql_connection(self._connection_data)
            if self.database:
                self.change_db(self.database)
            return True
        except errors.OperationalError as e:
            self._retry_count += 1
            time.sleep(1)
            return self._retry_connection()

    def _extract_host(self, host):
        if host.startswith('unix://'):
            protocol = 'unix'
            hostname = host[7:]
        else:
            protocol = 'tcp'
            hostname = host[6:]

        return (protocol, hostname)

    @property
    def host(self):
        protocol, host = self._extract_host(self._connection_data['host'])
        return host

    @property
    def port(self):
        return self._connection_data['port']

    def close(self):
        return self.con.close()

    @property
    def cursor(self):
        return self.con.cursor(buffered=True)

    def query(self, query, params=None):
        self.query_log.append((query, params))
        self.log_debug('Query: %s. Params: %s', str(query), str(params))
        try:
            cursor = self.cursor
            cursor.execute(query, params=params)
            return cursor
        except errors.OperationalError as e:
            # Retry connection if exception is "MySQL Connection not available"
            self.log_exception('Query exception: %s', e)
            if self._retry_connection():
                return self.query(query, params=params)
            raise e
        except errors.Error as e:
            self.log_exception('Query exception: %s', e)
            raise e

    def change_db(self, name):
        query = 'USE {0}'.format(name);
        self.query(query);
        self.database = name

    def is_fatal_error(self, error):
        if isinstance(error, errors.OperationalError):
            return True

        if isinstance(error, errors.InterfaceError):
            return True

        if isinstance(errors, errors.NotSupportedError):
            return True

        return False

    @classmethod
    def factory(cls, connection_data, session_name=None):
        try:
            instance = cls(connection_data, session_name)
        except mysql.connector.Error as err:
            logger.exception('Connection exception %s', err)
            return (None, err)
        return (instance, None)

    @classmethod
    def test(cls, connection_data):
        connection, err = cls.factory(connection_data)
        if connection is None:
            return (False, str(err))
        connection.close()
        return (True, None)
