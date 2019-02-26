#!/usr/bin/env python3
import os
import sys
import argparse

import mitzasql.constants as const

macros = [
        'create_first_session',
        'connect_to_localhost_from_sessions_list',
        'test_localhost_connection'
        ]

def get_macro_path(name):
    macro_path = os.path.dirname(os.path.realpath(__file__))
    macro_path = os.path.sep.join([macro_path, name + '.txt'])
    return macro_path

def create_first_session_handler():
    macro_path = get_macro_path('create_first_session')
    return (const.APP_NAME, '--sessions_file', '/dev/null', '--macro', macro_path)

def test_localhost_connection_handler():
    macro_path = get_macro_path('test_localhost_connection')
    return (const.APP_NAME, '--macro', macro_path)

def run_macro(name):
    try:
        handler = getattr(sys.modules[__name__], name + '_handler')
        process_arguments = handler()
    except AttributeError:
        process_arguments = (const.APP_NAME, '--macro', get_macro_path(name))
    sys.stdout.flush()
    os.execvp(const.APP_NAME, process_arguments)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('macro', help='Run specific macro', nargs='?')
    parser.add_argument('--list', help='Show configured macros',
            action='store_true')

    args = parser.parse_args()
    if args.list is False and args.macro is None:
        parser.print_help()
        sys.exit(0)

    if args.list:
        print('\n'.join(macros))
        sys.exit(1)

    if args.macro:
        run_macro(args.macro)
