# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

from ..logger import logger

class PyperclipStub:
    def copy(self, text):
        logger.warning('Unable to copy to clipboard: pyperclip module is not installed')

    def paste(self):
        logger.warning('Unable to paste from clipboard: pyperclip module is not installed')

pyperclip = None
try:
    import pyperclip
except ModuleNotFoundError:
    pyperclip = PyperclipStub()

def copy(text):
    try:
        pyperclip.copy(text)
    except Exception as e:
        logger.exception(e)

def paste():
    try:
        return pyperclip.paste()
    except Exception as e:
        logger.exception(e)
