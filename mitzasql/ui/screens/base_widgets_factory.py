# Copyright (c) 2021 Vlad Balmos <vladbalmos@yahoo.com>
# Author: Vlad Balmos <vladbalmos@yahoo.com>
# See LICENSE file

import urwid

class BaseWidgetsFactory:
    def __init__(self, state_machine):
        self._state_machine = state_machine

        # Contains signal name, handler and parameters for each created widget
        # Used by the destructor to disconnect any event handlers
        self._signal_handlers = []

        # Widgets cache
        self._widgets = {}
        self._factory_methods = self._get_factory_methods()

    def _get_factory_methods(self):
        raise NotImplementedError()

    def __del__(self):
        while True:
            try:
                obj, name, callback, kwargs = self._signal_handlers.pop()
                urwid.disconnect_signal(obj, name, callback, **kwargs)
            except IndexError:
                break

    def change_fsm_state(self, input, *args, **kwargs):
        self._state_machine.change_state(input, *args, **kwargs)

    def create(self, name, *args, **kwargs):
        cache_widget = True
        if 'cache' in kwargs:
            cache_widget = kwargs['cache']
            del kwargs['cache']

        if name not in self._widgets or cache_widget is False:
            factory_method = self._factory_methods[name]
            widget = factory_method(*args, **kwargs)

            if cache_widget is False:
                return widget
            self._widgets[name] = widget
        else:
            # Refresh the widget if it was cached
            widget = self._widgets[name]
            refresh_method = getattr(widget, 'refresh', None)
            if callable(refresh_method):
                refresh_method(*args, **kwargs)
        return widget

    def _connect_signal(self, obj, name, callback, **kwargs):
        key = urwid.connect_signal(obj, name, callback, **kwargs)
        self._signal_handlers.append((obj, name, callback, kwargs))

