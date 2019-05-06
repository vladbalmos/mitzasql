#!/usr/bin/env python3

import os
import sys
import tempfile
import time
from multiprocessing import Process

import mitzasql.constants as const

test_sessions_file = os.path.join(tempfile.gettempdir(),
        'mitzasql-ui-test-sessions' + str(time.time()) + '.ini')

def get_macro_path(name):
    macro_path = os.path.dirname(os.path.realpath(__file__))
    macro_path = os.path.sep.join([macro_path, name + '.txt'])
    return macro_path

tests = [
        {
            'name': 'Show version',
            'arguments': ['--version']
        },
        {
            'name': 'Exit without creating a session',
            'arguments': ['--macro', get_macro_path('01-exit-without-session'),
                '--sessions_file', '/dev/null']
        },
        {
            'name': 'Create session and exit',
            'arguments': ['--macro', get_macro_path('02-create-session-and-exit'),
                '--sessions_file', '/dev/null']
        },
        {
            'name': 'Create 3 sessions, edit the 2nd and delete the 3rd',
            'arguments': ['--macro', get_macro_path('03-create-edit-delete'),
                '--sessions_file', '/dev/null']
        },
        {
            'name': 'Create session and connect',
            'arguments': ['--macro', get_macro_path('04-create-and-connect'),
                '--sessions_file', test_sessions_file]
        },
        {
            'name': 'Navigate the databases view',
            'arguments': ['--macro', get_macro_path('05-navigate-db-view'),
                '--sessions_file', test_sessions_file]
        },
        {
            'name': 'Navigate the sakila database view',
            'arguments': ['--macro', get_macro_path('06-navigate-sakila-db-view'),
                '--sessions_file', test_sessions_file]
        },
    ]

class MitzasqlProcess(Process):

    def __init__(self, arguments):
        self.arguments = arguments
        self.arguments.insert(0, const.APP_NAME)
        super().__init__()

    def run(self):
        sys.stdout.flush()
        os.execvp(const.APP_NAME, self.arguments)


if __name__ == '__main__':
    for test in tests:
        print('Running "{0}"...'.format(test['name']))

        proc = MitzasqlProcess(test['arguments'])
        proc.start()
        proc.join(None)

        if proc.exitcode > 0:
            print('Failed to run test "{0}" with arguments\n {1}'.format(test['name'],
                test['arguments']), file=sys.stderr)
            sys.exit(1)
