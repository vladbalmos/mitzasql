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

"""States for the session select screen"""
STATE_INITIAL = 'initial'
STATE_SHOW_CREATE_SESSION_DIALOG = 'create_session_dialog'
STATE_SHOW_EDIT_SESSION_FORM = 'show_edit_session_form'
STATE_SHOW_SESSIONS_LIST = 'show_sessions_list'
STATE_SAVE_SESSION = 'save_session'
STATE_DELETE_SESSION = 'delete_session'
STATE_TEST_CONNECTION = 'test_connection'
STATE_CONNECT = 'connect'
STATE_CANCEL_EDIT_SESSION = 'cancel_edit_session'
STATE_SHOW_CONNECT_ERROR = 'connection_error'
STATE_QUIT = 'quit'
