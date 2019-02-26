import pytest

from mitzasql.db.model import Model


@pytest.fixture
def basic_dataset():
    return [(1, 2, 3), (4, 5, 6), (7, 8, 9)]

@pytest.fixture
def basic_columns():
    return (
            {
            'name': 'first_no',
            'is_int': 1,
            'flags': None
            },
            {
            'name': 'second_no',
            'is_int': 1,
            'flags': None
            },
            {
            'name': 'third_no',
            'is_int': 1,
            'flags': None
            }
        )

def test_model_returns_correct_rowcount(basic_dataset, basic_columns):
    model = Model(basic_dataset, basic_columns)
    assert len(model) == 3

def test_model_returns_item(basic_dataset, basic_columns):
    model = Model(basic_dataset, basic_columns)
    assert model[1] == (4, 5, 6)

def test_model_returns_correct_column_index(basic_dataset, basic_columns):
    model = Model(basic_dataset, basic_columns)
    assert model.col_index('second_no') == 1

def test_model_searches_for_keyword(basic_dataset, basic_columns):
    model = Model(basic_dataset, basic_columns)
    result = model.search('4', 0)
    assert result is not None

    row_index, row = result
    assert row_index == 1
    assert row == (4, 5, 6)

def test_model_searches_for_keyword_in_reverse(basic_dataset, basic_columns):
    model = Model(basic_dataset, basic_columns)
    result = model.search('4', 0, pos=2, reverse=True)
    assert result is not None

    row_index, row = result
    assert row_index == 1
    assert row == (4, 5, 6)

def test_model_search_returns_none_in_reverse(basic_dataset, basic_columns):
    model = Model(basic_dataset, basic_columns)
    result = model.search('8', 1, pos=1, reverse=True)
    assert result is None
