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

import os
import logging

from mitzasql import constants as const

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
