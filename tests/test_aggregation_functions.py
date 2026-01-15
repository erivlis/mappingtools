from mappingtools.aggregation import ema_aggregator, max_aggregator, min_aggregator


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
