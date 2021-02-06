# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import shutil
import os
import json
import hashlib
import pickle

from .. import constants

class SchemaCache:
    """
    Handles caching column widths to disk in order to preserve manual column
    resizes when the application is stopped.
    """
    def __init__(self, cache_path):
        self._cache_path = cache_path
        self._init_cache_path()

    def _init_cache_path(self):
        if not os.path.isdir(self._cache_path):
            os.makedirs(self._cache_path, exist_ok=True)

    def _get_cache_file(self, model):
        model_name = None
        if model.__class__.__name__ == 'DBTablesModel':
            model_name = model.__class__.__name__
        elif model.__class__.__name__ == 'TableModel':
            model_name = model.table_name
        else:
            # Dynamic query models are not cached
            return None

        if model.connection_name is None:
            # Anonymous sessions are not saved
            return None

        m = hashlib.sha256()
        m.update(model.connection_name.encode('utf-8') +
                model.database.encode('utf-8'))
        hash_ = m.hexdigest()
        return os.path.join(self._cache_path, hash_)

    def cache_col_width(self, model, col_index, width):
        cache_file = self._get_cache_file(model)
        if cache_file is None:
            return

        cached_widths = self.get_cached_widths(model)
        if cached_widths is None:
            cached_widths = {}

        try:
            column = model.columns[col_index]
        except:
            return

        col_hash = self.get_column_hash(column)
        cached_widths[col_hash] = width

        try:
            with open(cache_file, 'w') as cache_file:
                json.dump(cached_widths, cache_file)
        except Exception:
            return

    def get_cached_widths(self, model):
        cache_file = self._get_cache_file(model)
        if cache_file is None:
            return

        try:
            with open(cache_file) as cache_file:
                data = json.load(cache_file)
                return data
        except Exception:
            return

    def get_column_hash(self, column):
        column_data = { key: column[key] for key in column if key != 'max_len' }
        serialized = pickle.dumps(column_data)
        m = hashlib.sha256()
        m.update(serialized)
        hash_ = m.hexdigest()
        return hash_

    def clear(self):
        """
        Remove all cache files
        """
        try:
            shutil.rmtree(self._cache_path)
            self._init_cache_path()
        except Exception:
            return

schema_cache_instance = SchemaCache(constants.DEFAULT_CACHE_PATH)
