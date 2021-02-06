# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import configparser
import os

from . import constants as const

class SessionsRegistry:
    """
    Registry for MySQL connections settings.

    It reads the `sessions_file` for the previously saved sessions.
    Newly created sessions are written to the same file.
    """
    instance = None

    def __init__(self, sessions_file=None):
        self._sessions = configparser.RawConfigParser()
        if sessions_file is None:
            self._sessions_file = const.DEFAULT_SESSIONS_FILE
        else:
            self._sessions_file = sessions_file

        if not os.path.isdir(os.path.dirname(self._sessions_file)):
            os.makedirs(os.path.dirname(self._sessions_file), mode=0o700,
                    exist_ok=True)
        self._sessions.read(self._sessions_file)

    @property
    def sessions(self):
        return self._sessions.sections()

    def has_session(self, name):
        return self._sessions.has_section(name)

    def create_session(self, name, settings):
        """Add a new session to the registry

        Parameters:
        name:String The name of the session
        settings:dict The connection details:
                        settings = {
                        host: String,
                        port: String,
                        username: String,
                        password: String,
                        database: String
                        }
        """
        string_settings = {key: str(value) for key, value in settings.items()}
        self._sessions[name] = string_settings

    def __getitem__(self, name):
        return dict(self._sessions.items(name))

    def is_empty(self):
        return len(self._sessions.sections()) == 0

    def save(self):
        with open(self._sessions_file, 'w') as sessions_file:
            self._sessions.write(sessions_file)

    def add(self, connection_data):
        name = connection_data['name'];
        del connection_data['name']
        self._sessions[name] = connection_data

    def edit(self, session_name, connection_data):
        new_name = connection_data['name']
        del connection_data['name']

        if session_name != new_name:
            del self._sessions[session_name]
            connection_data['name'] = new_name
            return self.add(connection_data)

        self._sessions[session_name] = connection_data

    def __delitem__(self, name):
        del self._sessions[name]

    @classmethod
    def get_instance(cls, sessions_file=None):
        if cls.instance is None:
            cls.instance = SessionsRegistry(sessions_file=sessions_file)
        return cls.instance

