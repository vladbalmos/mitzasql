# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid
import time

from .. import utils
from ...history import History
from ...db.model import (TableModel, QueryModel)
from ...db.schema_cache import schema_cache_instance
from ...autocomplete.engine import SQLAutocompleteEngine
from .db_view_footer import DBViewFooter
from .query_widget import QueryWidget

class BaseDBView(urwid.Frame):
    SIGNAL_ACTION_EXIT = 'exit'
    SIGNAL_ACTION_HELP = 'help'
    SIGNAL_ACTION_RUN_QUERY = 'query_editor'
    SIGNAL_ACTION_QUERY_LOG = 'query_log'
    SIGNAL_ACTION_REFRESH = 'refresh'
    SIGNAL_ACTION_QUIT = 'quit'
    SIGNAL_MODEL_ERROR = 'model_error'
    SIGNALS = [SIGNAL_ACTION_EXIT, SIGNAL_ACTION_RUN_QUERY, SIGNAL_MODEL_ERROR]

    QUERY_HISTORY = History()

    TABLE_HEIGHT = 70
    EDITOR_HEIGHT = 20

    def __init__(self, model, connection, actions=[]):
        self._model = model
        self._model_error_handler = None
        self._table = None
        self._query_editor = None
        self._sql_autocomplete_engine = SQLAutocompleteEngine(model)
        self._connection = connection
        self._schema_cache = schema_cache_instance

        self._actions = []
        self._actions_to_signals = {}
        default_actions = [
               ('F1', u'F1 Help', self.SIGNAL_ACTION_HELP),
               ('F2', u'F2 Query Editor'),
               ('F4', u'F4 Log', self.SIGNAL_ACTION_QUERY_LOG),
               ('F5', u'F5 Refresh', self.SIGNAL_ACTION_REFRESH),
               ('F10', u'F10 Quit', self.SIGNAL_ACTION_QUIT)
               ]
        default_actions.extend(actions)
        self._prepare_actions_and_signals(default_actions)

        header = self._make_header()
        body = self._make_body()
        footer = self._make_footer()

        self._cmd_history_pending_cmd = None

        super().__init__(body, header, footer)
        signals = self.SIGNALS
        signals.extend(self._actions_to_signals.values())
        urwid.register_signal(self.__class__, signals)
        urwid.connect_signal(self, self.SIGNAL_ACTION_REFRESH,
                self.refresh_model)
        self._connect_model_signals()
        self._update_breadcrumbs()

    def _connect_model_signals(self):
        urwid.connect_signal(self._model, self._model.SIGNAL_ERROR,
                self.emit_model_error)
        urwid.connect_signal(self._model, self._model.SIGNAL_PRE_LOAD,
                self.toggle_loading_status, user_args=[True])
        urwid.connect_signal(self._model, self._model.SIGNAL_NEW_DATA,
                self.toggle_loading_status, user_args=[False])
        urwid.connect_signal(self._model, self._model.SIGNAL_LOAD,
                self.toggle_loading_status, user_args=[False])

    def _disconnect_model_signals(self):
        urwid.disconnect_signal(self._model, self._model.SIGNAL_PRE_LOAD,
                self.toggle_loading_status, user_args=[True])
        urwid.disconnect_signal(self._model, self._model.SIGNAL_NEW_DATA,
                self.toggle_loading_status, user_args=[False])
        urwid.disconnect_signal(self._model, self._model.SIGNAL_LOAD,
                self.toggle_loading_status, user_args=[False])
        urwid.disconnect_signal(self._model, self._model.SIGNAL_ERROR,
                self.emit_model_error)

    def __del__(self):
        self._disconnect_model_signals()
        urwid.disconnect_signal(self, self.SIGNAL_ACTION_REFRESH,
                self.refresh_model)
        self._disconnect_model_signals()
        self._model = None
        self._connection = None

    @property
    def model(self):
        return self._model

    def emit_model_error(self, model, error):
        urwid.emit_signal(self, self.SIGNAL_MODEL_ERROR, self, model, error)

    def set_model_error_handler(self, handler):
        if not self._model_error_handler:
            self._model_error_handler = handler
            urwid.connect_signal(self, self.SIGNAL_MODEL_ERROR, handler)

        if self._model.last_error is not None:
            self.emit_model_error(self._model, self._model.last_error)

    def toggle_loading_status(self, status, *args, **kwargs):
        self._footer.toggle_message_bar(status, message=u'Loading...')

    def refresh_model(self, emitter, action):
        self._model.reload()

    def _make_header(self):
        header = urwid.AttrMap(urwid.Text('', wrap='clip'), 'session_header')
        return header

    def _update_breadcrumbs(self):
        if self._connection.is_tcp is True:
            host = '{0}:{1}'.format(self._connection.host,
                    str(self._connection.port))
        else:
            host = self._connection.host

        session_name = self._connection.session_name

        breadcrumbs = []

        if session_name is not None:
            breadcrumbs.append(u'{0}({1})'.format(session_name, host))
        else:
            breadcrumbs.append(u'{0}'.format(host))

        if self._connection.database is not None:
            breadcrumbs.append(self._connection.database)

        if isinstance(self._model, TableModel):
            breadcrumbs.append(self._model.table_name)

        if isinstance(self._model, QueryModel):
            breadcrumbs.append(u'Query')

        breadcrumbs = '/'.join(breadcrumbs)
        utils.orig_w(self._header).set_text(u'[{0}]'.format(breadcrumbs))

    def _make_footer(self):
        command_processor = getattr(self, '_command_processor', None)
        footer = DBViewFooter(self._actions,
                command_processor=command_processor)
        urwid.connect_signal(footer, footer.SIGNAL_EXIT_COMMAND_MODE,
                self.exit_command_mode)
        return footer

    def _make_body(self):
        table = self._table_widget_cls(self._model)

        urwid.connect_signal(table, table.SIGNAL_COLUMN_RESIZED,
                self.on_resize_table_column)

        self._table = table
        self._query_editor = QueryWidget(autocomplete_engine=self._sql_autocomplete_engine)
        urwid.connect_signal(self._query_editor, self._query_editor.SIGNAL_LOADING_SUGGESTIONS, self.toggle_loading_status, user_args=[True])
        urwid.connect_signal(self._query_editor, self._query_editor.SIGNAL_LOADED_SUGGESTIONS, self.toggle_loading_status, user_args=[False])

        pile = urwid.Pile([('weight', BaseDBView.TABLE_HEIGHT, table), ('weight', 0,
            self._query_editor)])
        return pile

    def on_resize_table_column(self, emitter, col_index, new_width):
        '''
        Persist the new width to disk
        '''
        self._schema_cache.cache_col_width(emitter.model, col_index, new_width)

    def _prepare_actions_and_signals(self, actions):
        _actions = []
        actions_to_signals = {}
        for action in actions:
            if len(action) == 3:
                key, action, signal = action
            else:
                key, action = action
                signal = None

            _actions.append((key, action))

            if signal is not None:
                actions_to_signals[key] = signal

        self._actions = sorted(_actions, key=lambda action: int(action[0][1:]))
        self._actions_to_signals = actions_to_signals

    def keypress(self, size, key):
        result = super().keypress(size, key)
        if result is None:
            return None

        for action_key, action_name in self._actions:
            if action_key.lower() == key.lower():
                if action_key in self._actions_to_signals:
                    signal = self._actions_to_signals[action_key]
                    urwid.emit_signal(self, signal, self, action_name)
                    return

        if key == 'esc':
            if self._focus_is('table'):
                urwid.emit_signal(self, self.SIGNAL_ACTION_EXIT, self)
            else:
                self._toggle_query_editor()
            return

        if hasattr(self, '_command_processor'):
            if key == 'q':
                if self._cmd_history_pending_cmd is None:
                    self._cmd_history_pending_cmd = (key, time.time())
                    return;

            if key == ':' and self._cmd_history_pending_cmd is not None:
                _none, last_key_press = self._cmd_history_pending_cmd
                now = time.time()
                self._cmd_history_pending_cmd  = None
                if (now - last_key_press) < 500:
                    if len(self._command_processor.history) > 0:
                        self._enter_command_mode(key, show_last_cmd=True)
                    return

            if self._command_processor.is_string_comand(key):
                self._enter_command_mode(key)
                return

            if self._command_processor.is_key_command(key):
                self._command_processor.execute(cmd_key=key)
                return

        # Show query editor
        if key == 'f2':
            if self._focus_is('table') and self._editor_is_visible():
                self._switch_focus('editor')
            else:
                self._toggle_query_editor()
            return

        # Run query
        if key == 'f9':
            if self._focus_is('editor') and self._editor_is_visible():
                self._run_query()
            return

        # Show previous query
        if key == 'ctrl p':
            if self._focus_is('editor') and self._editor_is_visible():
                self._show_prev_query()
            return

        # Show next query
        if key == 'ctrl n':
            if self._focus_is('editor') and self._editor_is_visible():
                self._show_next_query()
            return

        # Clear editor
        if key == 'ctrl f9':
            if self._focus_is('editor') and self._editor_is_visible():
                self._query_editor.clear()
            return

        if key == 'shift ctrl up':
            self._resize_query_editor(True)
            return

        if key == 'shift ctrl down':
            self._resize_query_editor(False)
            return

        return key

    def _resize_query_editor(self, bigger_size):
        if not self._editor_is_visible():
            return

        table, tsize = self._body.contents[0]
        editor, esize = self._body.contents[1]

        if bigger_size:
            increment = 5
        else:
            increment = -5

        tsize_height = tsize[1] - increment
        esize_height = esize[1] + increment
        focus_position = self._body.focus_position

        if bigger_size and tsize_height < 40:
            return

        if not bigger_size and tsize_height > 75:
            return

        BaseDBView.TABLE_HEIGHT = tsize_height
        BaseDBView.EDITOR_HEIGHT = esize_height

        self._body.contents[0] = (table, (tsize[0], tsize_height))
        self._body.contents[1] = (editor, (esize[0], esize_height))

    def _editor_is_visible(self):
        widget, size = self._body.contents[1]
        return size[1] != 0

    def _run_query(self):
        query = self._query_editor.query
        self.QUERY_HISTORY.append(query)
        urwid.emit_signal(self, self.SIGNAL_ACTION_RUN_QUERY, self, query)

    def _show_prev_query(self):
        query = self.QUERY_HISTORY.prev
        if not query:
            return
        self._query_editor.query = query

    def _show_next_query(self):
        query = self.QUERY_HISTORY.next
        if not query:
            return
        self._query_editor.query = query

    def _toggle_query_editor(self):
        widget, size = self._body.contents[1]
        if size[1] == 0:
            new_size = ('weight', BaseDBView.EDITOR_HEIGHT)
            focus_pos = 1
        else:
            new_size = ('weight', 0)
            focus_pos = 0
        self._body.contents[1] = (widget, new_size)
        self._body.focus_position = focus_pos

    def _focus_is(self, widget_name):
        focus_pos = self._body.focus_position
        if focus_pos == 0:
            return widget_name == 'table'

        return widget_name == 'editor'

    def _switch_focus(self, widget_name):
        if widget_name == 'table':
            self._body.focus_position = 0
            return
        self._body.focus_position = 1

    def _enter_command_mode(self, key, show_last_cmd=False):
        self.focus_position = 'footer'
        self._footer.toggle_command_mode(True, key, show_last_cmd=show_last_cmd)

    def exit_command_mode(self, *args, **kwargs):
        self.focus_position = 'body'
