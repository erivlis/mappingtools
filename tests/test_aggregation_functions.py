from mappingtools.aggregation import ema_aggregator, last_aggregator, max_aggregator, min_aggregator


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
