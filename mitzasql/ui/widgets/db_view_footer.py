# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import threading

import urwid

from ...logger import logger
from .. import main_loop as shared_main_loop
from .. import utils
from .action_bar import ActionBar
from .command_edit import CommandEdit

class DBViewFooter(urwid.WidgetPlaceholder):
    SIGNAL_EXIT_COMMAND_MODE = 'exit_command_mode'
    def __init__(self, actions, command_processor=None):
        self._action_bar = urwid.AttrMap(ActionBar(actions), 'action_bar')
        self._message_bar = urwid.AttrMap(urwid.Text(''),
                'info_message')
        self._command_bar = None
        self._command_processor = None
        self._clear_error_timer = None

        if command_processor is not None:
            self._command_processor = command_processor
            command_bar = CommandEdit(command_processor)
            self._command_bar = urwid.AttrMap(command_bar,
                    'command_bar')
            urwid.connect_signal(command_bar, command_bar.SIGNAL_CANCEL, self.cancel_command_edit)
            urwid.connect_signal(command_processor, command_processor.SIGNAL_ERROR,
                    self.show_command_error)

        super().__init__(self._action_bar)
        urwid.register_signal(self.__class__, self.SIGNAL_EXIT_COMMAND_MODE)

    def __del__(self):
        self._cancel_clear_error_timer()
        if not self._command_bar:
            return
        command_bar = utils.orig_w(self._command_bar)
        urwid.disconnect_signal(command_bar, command_bar.SIGNAL_CANCEL, self.cancel_command_edit)
        urwid.disconnect_signal(self._command_processor,
                self._command_processor.SIGNAL_ERROR, self.show_command_error)

    def _cancel_clear_error_timer(self):
        if self._clear_error_timer is not None:
            self._clear_error_timer.cancel()

    def show_command_error(self, emitter, error_message, *args):
        self.toggle_message_bar(True, message=error_message, is_error=True)

        self._cancel_clear_error_timer()
        def clear_message():
            self.toggle_message_bar(False)

        self._clear_error_timer = threading.Timer(1, clear_message)
        self._clear_error_timer.daemon = True
        self._clear_error_timer.start()

    def toggle_message_bar(self, status, message=None, is_info=True,
            is_error=False):
        if status is False:
            self.original_widget = self._action_bar
            shared_main_loop.refresh()
            return

        self.original_widget = self._message_bar
        if message is not None:
            utils.orig_w(self._message_bar).set_text(message)
            if is_error is True:
                self._message_bar.set_attr_map({
                    None: 'error_message'
                    })
            else:
                self._message_bar.set_attr_map({
                    None: 'info_message'
                    })
        shared_main_loop.refresh()

    def cancel_command_edit(self, emiter):
        self.toggle_command_mode(False)
        urwid.emit_signal(self, self.SIGNAL_EXIT_COMMAND_MODE, self)

    def toggle_command_mode(self, status, command_marker=None,
            show_last_cmd=False):
        if status is True:
            self._cancel_clear_error_timer()
            self.original_widget = self._command_bar
            if show_last_cmd is True:
                utils.orig_w(self._command_bar).show_last_cmd()
            utils.orig_w(self._command_bar).set_marker(command_marker)
            return
        utils.orig_w(self._command_bar).reset()
        self.original_widget = self._action_bar

