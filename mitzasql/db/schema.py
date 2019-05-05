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

import sys
from collections import OrderedDict

import mysql.connector.errors as errors
from mysql.connector import (FieldType, FieldFlag)

# Column types
int_ctypes = ['int', 'tinyint', 'smallint', 'mediumint', 'bigint', 'bit']
real_ctypes = ['float', 'double', 'decimal']
text_ctypes = ['char', 'varchar', 'tinytext', 'text', 'mediumtext', 'longtext',
        'json', 'enum', 'set']
binary_ctypes = ['binary', 'varbinary', 'tinyblob', 'blob', 'mediumblob',
        'longblob']
temporal_ctypes = ['date', 'time', 'year', 'datetime', 'timestamp']
spatial_ctypes = ['point', 'linestring', 'polygon', 'geometry', 'multipoint',
        'multilinestring', 'multipolygon', 'geometrycollection']

# Field types
int_ftypes = [FieldType.TINY, FieldType.SHORT, FieldType.LONG,
        FieldType.LONGLONG, FieldType.INT24, FieldType.BIT]
real_ftypes = [FieldType.DECIMAL, FieldType.NEWDECIMAL, FieldType.FLOAT, FieldType.DOUBLE]
text_ftypes = [FieldType.VARCHAR, FieldType.VAR_STRING, FieldType.ENUM,
        FieldType.SET, FieldType.STRING, FieldType.JSON]
binary_ftypes = [FieldType.TINY_BLOB, FieldType.MEDIUM_BLOB,
        FieldType.LONG_BLOB, FieldType.BLOB]
temporal_ftypes = [FieldType.TIMESTAMP, FieldType.TIME, FieldType.DATE,
        FieldType.YEAR, FieldType.DATETIME, FieldType.NEWDATE]
spatial_ftypes = [FieldType.GEOMETRY]

# The required number of chars to display a specific type
field_types_length = {
        FieldType.DECIMAL: 66,
        FieldType.TINY: 4,
        FieldType.SHORT: 6,
        FieldType.LONG: 11,
        FieldType.FLOAT: 12,
        FieldType.DOUBLE: 24,
        FieldType.NULL: 4,
        FieldType.TIMESTAMP: 19,
        FieldType.LONGLONG: 24,
        FieldType.INT24: 8,
        FieldType.DATE: 10,
        FieldType.TIME: 10,
        FieldType.DATETIME: 19,
        FieldType.YEAR: 4,
        FieldType.NEWDATE: 19,
        FieldType.VARCHAR: sys.maxsize,
        FieldType.BIT: sys.maxsize,
        FieldType.JSON: sys.maxsize,
        FieldType.NEWDECIMAL: 66,
        FieldType.ENUM: 32,
        FieldType.SET: 32,
        FieldType.TINY_BLOB: sys.maxsize,
        FieldType.MEDIUM_BLOB: sys.maxsize,
        FieldType.LONG_BLOB: sys.maxsize,
        FieldType.BLOB: sys.maxsize,
        FieldType.VAR_STRING: sys.maxsize,
        FieldType.STRING: sys.maxsize,
        FieldType.GEOMETRY: sys.maxsize
        }

# Types for which to detect their string representation length
auto_detect_field_type_length = [
        FieldType.LONGLONG,
        FieldType.DECIMAL,
        FieldType.DOUBLE,
        FieldType.VARCHAR,
        FieldType.BIT,
        FieldType.NEWDECIMAL,
        FieldType.ENUM,
        FieldType.SET,
        FieldType.VAR_STRING,
        FieldType.STRING,
        FieldType.GEOMETRY
        ]

class QuerySchema:
    def __init__(self, cursor, data_sample):
        self.cursor = cursor
        self.data = data_sample
        self.schema = {}

    @property
    def columns(self):
        '''Returns a dictionary containing the column names as keys and
        metadata as their value:

        columns['name'] = {
            'friendly_type': 'VAR_STRING',
            'driver_type': 127,
            'flags': { # dictionary of mysql flags }
        }

        '''
        columns = []

        column_index = 0
        for column_data in self.cursor.description:
            name = column_data[0]
            driver_type = column_data[1]
            flags = get_column_flags(column_data[7])

            column = {
                    'name': name,
                    'flags': flags
                    }

            try:
                c_type = self.schema[name]['type']
                column.update({
                        'is_int': c_type in int_ctypes,
                        'is_real': c_type in real_ctypes,
                        'is_text': c_type in text_ctypes,
                        'is_binary': c_type in binary_ctypes,
                        'is_temporal': c_type in temporal_ctypes,
                        'is_spatial': c_type in spatial_ctypes
                        })
            except KeyError as e:
                column.update({
                        'is_int': driver_type in int_ftypes,
                        'is_real': driver_type in real_ftypes,
                        'is_text': driver_type in text_ftypes,
                        'is_binary': driver_type in binary_ftypes,
                        'is_temporal': driver_type in temporal_ftypes,
                        'is_spatial': driver_type in spatial_ftypes
                        })

            try:
                max_len = self.schema[name]['max_len']
            except KeyError as e:
                max_len = None

            if max_len is None:
                if driver_type in auto_detect_field_type_length:
                    max_len = auto_detect_column_length(column_index, self.data)

                if max_len is None:
                    max_len = field_types_length[driver_type]

            if len(name) >= max_len:
                max_len = len(name)
            elif max_len > 66:
                max_len = 66

            # The max_len is used by the table widget as width for the the
            # columns. Even though this is related to the view logic, we do it
            # here to optimize the rendering
            column['max_len'] = max_len + 2
            columns.append(column)
            column_index += 1
        return columns

class TableSchema(QuerySchema):
    def __init__(self, connection, table_name):
        self._con = connection
        self._table_name = table_name
        self.schema = self._table_schema()
        self.cursor = None
        self.data = None

    def __iter__(self):
        for row in self.schema.items():
            yield row

    def column_is_text(self, type_):
        return type_ in text_ctypes

    def column_is_spatial(self, type_):
        return type_ in spatial_ctypes

    def _table_schema(self):
        query = '''
        SELECT
            column_name,
            column_default,
            is_nullable,
            data_type,
            character_maximum_length,
            numeric_precision,
            numeric_scale,
            character_set_name,
            collation_name,
            column_key,
            extra
        FROM `information_schema`.`columns`
        WHERE
            table_schema = %(db_name)s
            AND
            table_name = %(table_name)s
        ORDER BY ORDINAL_POSITION ASC
        '''
        cursor = self._con.query(query, {
            'db_name': self._con.database,
            'table_name': self._table_name
            })
        data = cursor.fetchall()
        schema = OrderedDict()
        for row in data:
            column_name, default, nullable, _type, char_max_len, num_precision, \
                    num_scale, charset, collation, key, extra = row

            if nullable == 'YES':
                nullable = True
            else:
                nullable = False

            schema[column_name] = {
                    'type': _type,
                    'charset': charset,
                    'collation': collation,
                    'default': default,
                    'nullable': nullable,
                    'key': key,
                    'extra': extra
                    }

            c_len = None
            if _type in int_ctypes or _type in real_ctypes:
                if num_precision is not None or num_scale is not None:
                    # Add 1 character to len to account for any coma that might exist
                    c_len = int(num_precision or 0) + int(num_scale or 0) + 1
            elif _type in text_ctypes or _type in binary_ctypes:
                if char_max_len is not None:
                    c_len = int(char_max_len)

            schema[column_name]['max_len'] = c_len
        return schema


def auto_detect_column_length(c_index, sample):
    '''Get the max length for the item in column `c_index` in the first
    `MAX_ROW_FOR_COLUMN_LENGTH_DETECTION`
    '''
    if len(sample) == 0:
        return None
    column = [str(r[c_index]) for r in sample]
    item = max(column, key=len)
    return len(item)


def get_column_flags(flag):
    flags = {}
    for name in FieldFlag.desc:
        (value, description) = FieldFlag.desc[name]
        if flag & value:
            flags[name] = {
                    'name': name,
                    'value': value,
                    'desc': description
                    }
    return flags
