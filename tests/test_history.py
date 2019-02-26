import pytest

from mitzasql.history import History

def test_history_returns_last_item():
    history = History()
    history.append('item1')
    history.append('item2')
    history.append('item3')

    last = history.last
    assert last == 'item3'

def test_history_returns_prev_and_next_items():
    history = History()
    history.append('item1')
    history.append('item2')
    history.append('item3')

    prev = history.prev
    assert prev == 'item3'
    prev = history.prev
    assert prev == 'item2'
    prev = history.prev
    assert prev == 'item1'

    next_ = history.next
    assert next_ == 'item2'
    next_ = history.next
    assert next_ == 'item3'
