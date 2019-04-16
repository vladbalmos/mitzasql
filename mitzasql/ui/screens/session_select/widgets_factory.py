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

import urwid

from mitzasql.ui.widgets.create_new_session_dialog import CreateNewSessionDialog
from mitzasql.ui.widgets.saved_sessions_list import SavedSessionsList
from mitzasql.ui.widgets.edit_session_form import EditSessionForm
from mitzasql.ui.screens.base_widgets_factory import BaseWidgetsFactory
from . import states

class WidgetsFactory(BaseWidgetsFactory):
    """Creates and caches widgets for the session select screen"""

    def _get_factory_methods(self):
        factory_methods = {}
        factory_methods['create_session_dialog'] = self.create_create_session_dialog
        factory_methods['sessions_list'] = self.create_sessions_list
        factory_methods['create_session_form'] = self.create_create_session_form

        return factory_methods

    def create_create_session_dialog(self):
        dialog = CreateNewSessionDialog()
        self._connect_signal(dialog, CreateNewSessionDialog.SIGNAL_YES,
                self.change_fsm_state, user_args=['yes'])
        self._connect_signal(dialog, CreateNewSessionDialog.SIGNAL_QUIT,
                self.change_fsm_state, user_args=['quit'])
        return dialog

    def create_sessions_list(self, sessions):
        list = SavedSessionsList(sessions)
        self._connect_signal(list, SavedSessionsList.SIGNAL_QUIT,
                self.change_fsm_state, user_args=['quit'])
        self._connect_signal(list, SavedSessionsList.SIGNAL_CREATE_NEW,
                self.change_fsm_state, user_args=['create'])
        self._connect_signal(list, SavedSessionsList.SIGNAL_CONNECT,
                self.change_fsm_state, user_args=['connect'])
        self._connect_signal(list, SavedSessionsList.SIGNAL_EDIT,
                self.change_fsm_state, user_args=['edit'])
        self._connect_signal(list, SavedSessionsList.SIGNAL_DELETE,
                self.change_fsm_state, user_args=['delete'])
        return list

    def create_create_session_form(self, form_data):
        form = EditSessionForm(form_data)
        self._connect_signal(form, form.SIGNAL_SAVE, self.change_fsm_state,
                user_args=['save'])
        self._connect_signal(form, form.SIGNAL_TEST, self.change_fsm_state,
                user_args=['test'])
        self._connect_signal(form, form.SIGNAL_CONNECT, self.change_fsm_state,
                user_args=['connect'])
        self._connect_signal(form, form.SIGNAL_CANCEL, self.change_fsm_state,
                user_args=['cancel'])
        return form
