# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import os
import logging

from . import constants as const

log_dir = os.path.dirname(const.DEFAULT_LOG_PATH)

os.makedirs(log_dir, mode=0o700, exist_ok=True)

logger = logging.getLogger(const.APP_NAME)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(const.DEFAULT_LOG_PATH, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(log_formatter)

logger.addHandler(file_handler)

class LoggerMixin:
    def set_log_prefix(self, prefix):
        self._prefix = prefix

    def _make_msg(self, msg):
        return self._prefix + ':' + msg

    def log_debug(self, msg, *args, **kwargs):
        msg = self._make_msg(msg)
        logger.debug(msg, *args, **kwargs)

    def log_info(self, msg, *args, **kwargs):
        msg = self._make_msg(msg)
        logger.info(msg, *args, **kwargs)

    def log_warning(self, msg, *args, **kwargs):
        msg = self._make_msg(msg)
        logger.warning(msg, *args, **kwargs)

    def log_error(self, msg, *args, **kwargs):
        msg = self._make_msg(msg)
        logger.error(msg, *args, **kwargs)

    def log_critical(self, msg, *args, **kwargs):
        msg = self._make_msg(msg)
        logger.critical(msg, *args, **kwargs)

    def log_exception(self, msg, *args, **kwargs):
        msg = self._make_msg(msg)
        logger.exception(msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        msg = self._make_msg(msg)
        logger.log(level, msg, *args, **kwargs)

def disable_logging():
    logger.removeHandler(file_handler)
    logger.addHandler(logging.NullHandler())
