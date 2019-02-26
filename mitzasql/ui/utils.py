import urwid

def orig_w(widget):
    if isinstance(widget, urwid.AttrMap):
        return widget.original_widget
    return widget
