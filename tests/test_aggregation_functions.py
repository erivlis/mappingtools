from collections import Counter

from mappingtools.aggregation import (
    all_aggregator,
    count_aggregator,
    distinct_aggregator,
    ema_aggregator,
    first_aggregator,
    last_aggregator,
    max_aggregator,
    min_aggregator,
    sum_aggregator,
)


def test_all_aggregator_direct():
    mapping = {'key': [1]}
    all_aggregator(mapping, 'key', [2, 3])
    assert mapping['key'] == [1, 2, 3]


def test_count_aggregator_direct():
    mapping = {'key': Counter({'a': 1})}
    count_aggregator(mapping, 'key', ['a', 'b', 'a'])
    assert mapping['key'] == Counter({'a': 3, 'b': 1})


def test_distinct_aggregator_direct():
    mapping = {'key': {1}}
    distinct_aggregator(mapping, 'key', [1, 2, 3, 2])
    assert mapping['key'] == {1, 2, 3}


def test_first_aggregator_direct():
    mapping = {}

    # Key does not exist, should take the first value
    first_aggregator(mapping, 'key', [10, 20, 30])
    assert mapping['key'] == 10

    # Key exists, should be completely ignored
    first_aggregator(mapping, 'key', [99, 100])
    assert mapping['key'] == 10


def test_sum_aggregator_direct():
    mapping = {}

    # Key does not exist
    sum_aggregator(mapping, 'key', [10, 20])
    assert mapping['key'] == 30

    # Key exists
    sum_aggregator(mapping, 'key', [5, 5])
    assert mapping['key'] == 40


def test_ema_aggregator_direct():
    mapping = {}

    # Key does not exist: first value becomes current_ema, subsequent values apply alpha=0.5
    # values: [10, 20]
    # step 1: current_ema = 10 (since it was None)
    # step 2: current_ema = (20 + 10) * 0.5 = 15.0
    ema_aggregator(mapping, 'key', [10, 20])
    assert mapping['key'] == 15.0

    # Key exists (currently 15.0)
    # value: [25]
    # current_ema = (25 + 15.0) * 0.5 = 20.0
    ema_aggregator(mapping, 'key', [25])
    assert mapping['key'] == 20.0


def test_max_aggregator_direct():
    mapping = {}

    # Test with empty values (Line 50)
    max_aggregator(mapping, 'key', [])
    assert 'key' not in mapping

    # Test with new key (Line 53)
    max_aggregator(mapping, 'key', [10])
    assert mapping['key'] == 10

    # Test with existing key
    max_aggregator(mapping, 'key', [20])
    assert mapping['key'] == 20

    # Test with generator (Line 48 - isinstance check)
    max_aggregator(mapping, 'gen', (x for x in [1, 2, 3]))
    assert mapping['gen'] == 3


def test_min_aggregator_direct():
    mapping = {}

    # Test with empty values (Line 67)
    min_aggregator(mapping, 'key', [])
    assert 'key' not in mapping

    # Test with new key (Line 70)
    min_aggregator(mapping, 'key', [10])
    assert mapping['key'] == 10

    # Test with existing key
    min_aggregator(mapping, 'key', [5])
    assert mapping['key'] == 5

    # Test with generator
    min_aggregator(mapping, 'gen', (x for x in [1, 2, 3]))
    assert mapping['gen'] == 1


def test_last_aggregator_direct():
    mapping = {}

    # Test with a Sequence (hits the fast path: `values[-1]`)
    last_aggregator(mapping, 'seq', [1, 2, 3])
    assert mapping['seq'] == 3

    # Test with an Iterator (hits the generic `for val in values: pass` fallback loop)
    def my_iterator():
        yield 10
        yield 20
        yield 30

    last_aggregator(mapping, 'iter', my_iterator())
    assert mapping['iter'] == 30

    # Test with an empty Iterator (should set to None)
    def empty_iterator():
        yield from []

    last_aggregator(mapping, 'empty_iter', empty_iterator())
    assert mapping['empty_iter'] is None
