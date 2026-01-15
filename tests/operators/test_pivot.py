import pytest

from mappingtools.aggregation import Aggregation
from mappingtools.operators import pivot


def test_pivot_basic():
    # Basic pivot: rows=A, cols=B, values=C
    data = [
        {'A': 'foo', 'B': 'one', 'C': 1},
        {'A': 'foo', 'B': 'two', 'C': 2},
        {'A': 'bar', 'B': 'one', 'C': 3},
    ]
    result = pivot(data, index='A', columns='B', values='C')
    assert result == {
        'foo': {'one': 1, 'two': 2},
        'bar': {'one': 3}
    }


def test_pivot_missing_keys():
    # Skip items missing keys
    data = [
        {'A': 'foo', 'B': 'one', 'C': 1},
        {'A': 'foo', 'C': 2},  # Missing B
    ]
    result = pivot(data, index='A', columns='B', values='C')
    assert result == {'foo': {'one': 1}}


def test_pivot_last_wins():
    # Default aggregation is LAST
    data = [
        {'A': 'foo', 'B': 'one', 'C': 1},
        {'A': 'foo', 'B': 'one', 'C': 2},
    ]
    result = pivot(data, index='A', columns='B', values='C')
    assert result == {'foo': {'one': 2}}


def test_pivot_first_wins():
    data = [
        {'A': 'foo', 'B': 'one', 'C': 1},
        {'A': 'foo', 'B': 'one', 'C': 2},
    ]
    result = pivot(data, index='A', columns='B', values='C', aggregation=Aggregation.FIRST)
    assert result == {'foo': {'one': 1}}


def test_pivot_sum():
    data = [
        {'A': 'foo', 'B': 'one', 'C': 1},
        {'A': 'foo', 'B': 'one', 'C': 2},
    ]
    result = pivot(data, index='A', columns='B', values='C', aggregation=Aggregation.SUM)
    assert result == {'foo': {'one': 3}}


def test_pivot_count():
    # Count occurrences of values. Value itself doesn't matter for count, just presence.
    # But Aggregation.COUNT uses Counter.update({val: 1}).
    # So result[row][col] will be a Counter({val: count}).
    data = [
        {'A': 'foo', 'B': 'one', 'C': 'x'},
        {'A': 'foo', 'B': 'one', 'C': 'x'},
        {'A': 'foo', 'B': 'one', 'C': 'y'},
    ]
    result = pivot(data, index='A', columns='B', values='C', aggregation=Aggregation.COUNT)
    # result['foo']['one'] is a Counter
    assert result['foo']['one']['x'] == 2
    assert result['foo']['one']['y'] == 1


def test_pivot_all():
    # Collect all values into a list
    data = [
        {'A': 'foo', 'B': 'one', 'C': 1},
        {'A': 'foo', 'B': 'one', 'C': 2},
    ]
    result = pivot(data, index='A', columns='B', values='C', aggregation=Aggregation.ALL)
    assert result['foo']['one'] == [1, 2]


def test_pivot_distinct():
    # Collect distinct values into a set
    data = [
        {'A': 'foo', 'B': 'one', 'C': 1},
        {'A': 'foo', 'B': 'one', 'C': 1},
        {'A': 'foo', 'B': 'one', 'C': 2},
    ]
    result = pivot(data, index='A', columns='B', values='C', aggregation=Aggregation.DISTINCT)
    assert result['foo']['one'] == {1, 2}


def test_pivot_max():
    data = [
        {'A': 'foo', 'B': 'one', 'C': 1},
        {'A': 'foo', 'B': 'one', 'C': 5},
        {'A': 'foo', 'B': 'one', 'C': 2},
    ]
    result = pivot(data, index='A', columns='B', values='C', aggregation=Aggregation.MAX)
    assert result['foo']['one'] == 5


def test_pivot_min():
    data = [
        {'A': 'foo', 'B': 'one', 'C': 5},
        {'A': 'foo', 'B': 'one', 'C': 1},
        {'A': 'foo', 'B': 'one', 'C': 2},
    ]
    result = pivot(data, index='A', columns='B', values='C', aggregation=Aggregation.MIN)
    assert result['foo']['one'] == 1


def test_pivot_ema():
    # Logic:
    # 1. Add 1: 1.0 (First time)
    # 2. Add 2: (1.0 + 2) / 2 = 1.5
    # 3. Add 3: (1.5 + 3) / 2 = 2.25

    data = [
        {'A': 'foo', 'B': 'one', 'C': 1},
        {'A': 'foo', 'B': 'one', 'C': 2},
        {'A': 'foo', 'B': 'one', 'C': 3},
    ]
    result = pivot(data, index='A', columns='B', values='C', aggregation=Aggregation.EMA)
    assert result['foo']['one'] == pytest.approx(2.25)


def test_pivot_empty():
    assert pivot([], index='A', columns='B', values='C') == {}
