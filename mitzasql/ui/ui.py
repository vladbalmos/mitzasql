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
import sys
import signal
import time
import threading
import urwid
import re

from mitzasql.ui import theme
from mitzasql.ui import main_loop as shared_main_loop
from mitzasql.ui.builder import Builder

top_most_widget = None
palette = theme.get_palette()
builder = None
main_loop = None
simulate_input_pipe = None

def init():
    """Initialize the UI

    Creates an empty widget placeholder top most widget and initializes the
    screens builder with it
    """
    global top_most_widget, builder

    top_most_widget = urwid.WidgetPlaceholder(urwid.SolidFill(' '))
    builder = Builder(top_most_widget)

def build_screen(name, display, **kwargs):
    screen = builder.build_screen(name, display, **kwargs)
    return screen

def connect_signal(obj, name, callback, **kwargs):
    """Wrapper for urwid.connect_signal"""
    urwid.connect_signal(obj, name, callback, **kwargs)

def refresh():
    main_loop.draw_screen()

def convert_termsignals_to_exit_loop(signum, frame):
    raise urwid.ExitMainLoop()

def simulate_input(data):
    """Callback called when there's data in the main loop pipe

    Receives keys from the `simulate_input_thread` and sends input to the main
    loop

    Parameters:
    data:bytes array
    """
    if data.decode('utf-8') == 'remove_watch':
        main_loop.remove_watch_pipe(simulate_input_pipe)
        return
    main_loop.process_input([data.decode('utf-8')])

def simulate_input_thread(fd, macro_file):
    """Reads the macro file line by line and sends input to the main event loop
    through a pipe (fd)

    Parameters:
    fd:file descriptor The pipe to the main loop
    macro_file:String Path to macro file
    """
    with open(macro_file) as file:
        while True:
            line = file.readline()
            if line is '':
                break
            line = line.rstrip()
            input_type, *segments = line.split(':')
            if input_type.startswith('#'):
                continue
            if input_type == 'key':
                key = segments[0]
                if key == 'space':
                    key = ' '
                if len(segments) == 2:
                    repetitions = int(segments[1])
                else:
                    repetitions = 1
                for i in range(0, repetitions):
                    os.write(fd, key.encode('utf8'))
                    time.sleep(0.08)
            if input_type == 'key_sequence':
                sequence = ':'.join(segments)

                # Parse for environment variables placeholders
                matches = re.findall('({{.*?}})', sequence)
                for match in matches:
                    var_name = match[2:-2]
                    var_value = os.getenv(var_name, '')
                    sequence = sequence.replace(match, var_value)

                for char in sequence:
                    os.write(fd, char.encode('utf8'))
                    time.sleep(0.05)
            elif input_type == 'sleep':
                value = float(segments[0])
                time.sleep(value)
    os.write(fd, 'remove_watch'.encode('utf8'))
    time.sleep(0.1)
    os.close(fd)

def start_loop(macro_file=None):
    """Start ui event loop

    If `macro_file` is set create a new thread which reads the macro file and
    sends input to the main loop

    Parameters:
    macro_file:String Path to macrofile
    """
    global main_loop, simulate_input_pipe
    main_loop = urwid.MainLoop(top_most_widget,
            palette=palette,
            handle_mouse=False,
            pop_ups=True)
    main_loop.screen.set_terminal_properties(colors=256)

    if macro_file is not None:
        try:
            with open(macro_file) as file:
                pass
        except FileNotFoundError:
            print('Macro file does not exist!', file=sys.stderr)
            sys.exit(1)

        simulate_input_pipe = main_loop.watch_pipe(simulate_input)
        thread = threading.Thread(target=simulate_input_thread,
                args=[simulate_input_pipe, macro_file])
        thread.start()

    signal.signal(signal.SIGINT, convert_termsignals_to_exit_loop)
    signal.signal(signal.SIGQUIT, convert_termsignals_to_exit_loop)
    signal.signal(signal.SIGTERM, convert_termsignals_to_exit_loop)

    # Set a reference to the main loop in a another module
    # in order to avoid circular reference in widgets when
    # importing the ui to refresh the screen
    shared_main_loop.mutable['loop'] = main_loop
    main_loop.run()
