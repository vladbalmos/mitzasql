import os
import pytest

from mitzasql.db.connection import Connection

db_host = os.getenv('DB_HOST', 'tcp://localhost')
db_port = os.getenv('DB_PORT', '3306')
db_username = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASS', '')

@pytest.fixture(scope='module')
def connection():
    con_data = {
            'host': db_host,
            'port': db_port,
            'username': db_username,
            'password': db_password,
            'database': ''
            }
    con, error = Connection.factory(con_data, 'localhost')
    assert error is None
    return con

@pytest.fixture(scope='module')
def sakila_connection():
    con_data = {
            'host': db_host,
            'port': db_port,
            'username': db_username,
            'password': db_password,
            'database': 'sakila'
            }
    con, error = Connection.factory(con_data, 'localhost')
    assert error is None
    return con
