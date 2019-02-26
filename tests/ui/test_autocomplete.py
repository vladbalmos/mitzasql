import pytest

from mitzasql.ui.widgets.cmd_proc import Autocomplete

def test_autocomplete_returns_suggestions():
    suggestions = [
            'john',
            'johnny',
            'jake',
            'jane'
            ]

    autocomplete = Autocomplete(suggestions, 'joh')

    suggestion = autocomplete.suggestion('forward')
    assert suggestion == 'john'
    suggestion = autocomplete.suggestion('forward')
    assert suggestion == 'johnny'
    suggestion = autocomplete.suggestion('forward')
    assert suggestion == 'john'
    suggestion = autocomplete.suggestion('forward')
    assert suggestion == 'johnny'

    suggestion = autocomplete.suggestion('back')
    assert suggestion == 'john'
    suggestion = autocomplete.suggestion('back')
    assert suggestion == 'johnny'




