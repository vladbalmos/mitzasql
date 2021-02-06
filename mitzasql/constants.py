# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

"""Contains the constants used throughout the application"""
import os
import appdirs

APP_NAME = 'mitzasql'

SCREEN_SESSION_SELECT = 'session-select'
SCREEN_SESSION = 'session'

DEFAULT_CACHE_PATH = os.path.join(appdirs.user_cache_dir(APP_NAME), 'schema')
DEFAULT_LOG_PATH = os.path.join(appdirs.user_log_dir(APP_NAME),
        '{0}.log'.format(APP_NAME))
DEFAULT_SESSIONS_FILE = os.path.join(appdirs.user_config_dir(APP_NAME),
        'sessions.ini')
