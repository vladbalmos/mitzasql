import pytest
import urwid

from mitzasql.ui.widgets.table_view import TableView
from mitzasql.db.model import TableModel
from ..db.connection_fixture import sakila_connection

filters = [
        {
        'filter': ['eq', 'address_id', '1'],
        'count': 1
        },
        {
        'filter': ['neq', 'address_id', '1'],
        'count': 602
        },
        {
        'filter': ['lt', 'address_id', '10'],
        'count': 9
        },
        {
        'filter': ['lte', 'address_id', '10'],
        'count': 10
        },
        {
        'filter': ['gt', 'address_id', '600'],
        'count': 5
        },
        {
        'filter': ['gte', 'address_id', '600'],
        'count': 6
        },
        {
        'filter': ['in', 'address_id', '1,2, 3'],
        'count': 3
        },
        {
        'filter': ['nin', 'address_id', '1,2, 3'],
        'count': 600
        },
        {
        'filter': ['null', 'address2'],
        'count': 4
        },
        {
        'filter': ['nnull', 'address2'],
        'count': 599
        },
        {
        'filter': ['empty', 'address2'],
        'count': 599
        },
        {
        'filter': ['nempty', 'address2'],
        'count': 0
        },
        {
        'filter': ['like', 'address', '%hanoi%'],
        'count': 2
        },
        {
        'filter': ['nlike', 'address', '%hanoi%'],
        'count': 601
        },
        # {
        # 'filter': ['between', 'address_id', '1', '4'],
        # 'count': 4
        # },
        # {
        # 'filter': ['nbetween', 'address_id', '1', '4'],
        # 'count': 599
        # },
        ]

@pytest.fixture(params=filters)
def filter_cmd(request):
    return request.param

def test_view_filters_model(sakila_connection, filter_cmd):
    model = TableModel(sakila_connection, 'address')
    view = TableView(model, sakila_connection)

    assert len(view.model) == 603

    op, *args = filter_cmd['filter']
    expected_count = filter_cmd['count']

    view.filter(op, *args)
    assert len(view.model) == expected_count

def test_view_clears_model_filter(sakila_connection):
    model = TableModel(sakila_connection, 'address')
    view = TableView(model, sakila_connection)

    assert len(view.model) == 603

    view.filter('eq', 'address_id', '1')
    assert len(view.model) == 1

    view.filter('clearfilters')
    assert len(view.model) == 603
