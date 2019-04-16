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
from mitzasql.sessions_registry import SessionsRegistry
from mitzasql.logger import LoggerMixin
from mitzasql.ui import ui
from mitzasql.db.connection import Connection
import mitzasql.constants as const

class App(LoggerMixin):
    """Main application class

    Initializes the UI and loads the appropriate screen based on the parameters
    passed from the main script.
    """
    def __init__(self, session_name=None, sessions_file=None):
        ui.init()
        self._session_name = session_name;
        self._sessions_registry = SessionsRegistry.get_instance(sessions_file)
        self._screen = None
        self.connection = None
        self.set_log_prefix('APP')
        self._set_screen()

    def start_ui(self, macro_file=None):
        """Start the UI loop. If a macro file was given run the macro

        Parameters:
        macro_file:string Path to macro file
        """
        ui.start_loop(macro_file)

    def _set_screen(self):
        if self._session_name is None:
            self.log_debug('Showing the "select session" screen')
            screen = ui.build_screen(const.SCREEN_SESSION_SELECT, display=True,
                    **{'sessions_registry': self._sessions_registry})
            ui.connect_signal(screen, screen.SIGNAL_CONNECT,
                    self.create_connection)
            ui.connect_signal(screen, screen.SIGNAL_TEST_CONNECTION,
                    self.test_connection)
            self._screen = screen
            return;

        self.log_debug("Showing the database view")
        connection_data = self._sessions_registry[self._session_name]

        con, error_message = Connection.factory(connection_data,
                session_name=self._session_name)

        if error_message is not None:
            print("Unable to connect: {0}".format(error_message),
                    file=sys.stderr)
            sys.exit(1)

        screen = ui.build_screen(const.SCREEN_SESSION, display=True,
            connection=con)
        self._screen = screen

    def create_connection(self, select_session_screen, session_name=None,
            connection_data=None):
        """Create database connection and load the appropriate screen

        If `session_name` is valid, get the connection details from the
        registry, or else use the details from `connection_data`

        Parameters:
        select_session_screen:ui.screens.session_select.SessionSelect The screen that triggered the connect signal
        session_name:String The session name
        connection_data:dict The connection details

        """
        select_session_screen.set_progress(u'Connecting...')
        ui.refresh() # required because the next call will block the event loop

        if session_name is not None:
            connection_data = self._sessions_registry[session_name]

        con, error_message = Connection.factory(connection_data,
                session_name=session_name)
        if con is None:
            select_session_screen.set_connection_result(False,
                    str(error_message), session_name, connection_data)
            return

        self.connection = con
        screen = ui.build_screen(const.SCREEN_SESSION, display=True,
            connection=con)
        self._screen = screen

    def test_connection(self, select_session_screen, connection_data):
        """Test database connection

        Try to connect to the server using `connection_data`

        Paramters:
        select_session_screen:ui.screens.session_select.SessionSelect The screen that triggered the test signal
        connection_data:dict The connection details
        """

        select_session_screen.set_progress(u'Connecting...')
        ui.refresh() # required because the next call will block the event loop
        result, error_message = Connection.test(connection_data)

        if result is False:
            select_session_screen.set_connection_test_result(False,
                    error=error_message)
            return
        select_session_screen.set_connection_test_result(True)

    @classmethod
    def run(cls, session_name=None, macro=None, sessions_file=None):
        """Run the application"""
        instance = cls(session_name, sessions_file=sessions_file)
        instance.start_ui(macro)
        # Cleanup
        if instance.connection:
            instance.connection.close()
