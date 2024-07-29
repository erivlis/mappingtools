# Generated by CodiumAI
from collections import defaultdict

import pytest
from mappingtools import MappingCollector, MappingCollectorMode


# Initialization with default mode
def test_initialization_with_default_mode():
    # Arrange & Act
    collector = MappingCollector()
    # Assert
    assert collector.mode == MappingCollectorMode.ALL
    assert isinstance(collector._mapping, defaultdict)


# Initialization with each specific mode
def test_initialization_with_each_mode():
    # Arrange & Act & Assert
    collector_all = MappingCollector(MappingCollectorMode.ALL)
    assert isinstance(collector_all._mapping, defaultdict)

    collector_count = MappingCollector(MappingCollectorMode.COUNT)
    assert isinstance(collector_count._mapping, defaultdict)

    collector_distinct = MappingCollector(MappingCollectorMode.DISTINCT)
    assert isinstance(collector_distinct._mapping, defaultdict)

    collector_first = MappingCollector(MappingCollectorMode.FIRST)
    assert isinstance(collector_first._mapping, dict)

    collector_last = MappingCollector(MappingCollectorMode.LAST)
    assert isinstance(collector_last._mapping, dict)


# Adding key-value pairs in ALL mode
def test_adding_key_value_pairs_in_all_mode():
    # Arrange
    collector = MappingCollector(MappingCollectorMode.ALL)
    # Act
    collector.add('key1', 'value1')
    collector.add('key1', 'value2')
    # Assert
    assert collector.mapping['key1'] == ['value1', 'value2']


# Adding key-value pairs in COUNT mode
def test_adding_key_value_pairs_in_count_mode():
    # Arrange
    collector = MappingCollector(MappingCollectorMode.COUNT)
    # Act
    collector.add('key1', 'value1')
    collector.add('key1', 'value1')
    # Assert
    assert collector.mapping['key1']['value1'] == 2


# Adding key-value pairs in DISTINCT mode
def test_adding_key_value_pairs_in_distinct_mode():
    # Arrange
    collector = MappingCollector(MappingCollectorMode.DISTINCT)
    # Act
    collector.add('key1', 'value1')
    collector.add('key1', 'value1')
    # Assert
    assert collector.mapping['key1'] == {'value1'}


# Adding key-value pairs in FIRST mode
def test_adding_key_value_pairs_in_first_mode():
    # Arrange
    collector = MappingCollector(MappingCollectorMode.FIRST)
    # Act
    collector.add('key1', 'value1')
    collector.add('key1', 'value2')
    # Assert
    assert collector.mapping['key1'] == 'value1'


# Initialization with invalid mode
def test_initialization_with_invalid_mode():
    from mappingtools import MappingCollector
    # Arrange & Act & Assert
    with pytest.raises(ValueError):
        MappingCollector("INVALID_MODE")


# Adding key-value pairs with non-hashable keys
def test_adding_key_value_pairs_with_non_hashable_keys():
    # Arrange
    collector = MappingCollector(MappingCollectorMode.ALL)
    # Act & Assert
    with pytest.raises(TypeError):
        collector.add(['non-hashable'], 'value')


# Collecting from an empty iterable
def test_collecting_from_empty_iterable():
    # Arrange
    collector = MappingCollector(MappingCollectorMode.ALL)
    empty_iterable = []
    # Act
    collector.collect(empty_iterable)
    # Assert
    assert len(collector.mapping) == 0


# Adding duplicate keys in DISTINCT mode
def test_adding_duplicate_keys_in_distinct_mode():
    # Arrange
    collector = MappingCollector(MappingCollectorMode.DISTINCT)
    # Act
    collector.add('key1', 'value1')
    collector.add('key1', 'value2')
    collector.add('key1', 'value2')
    # Assert
    assert collector.mapping['key1'] == {'value1', 'value2'}


# Adding duplicate keys in FIRST mode
def test_adding_duplicate_keys_in_first_mode():
    # Arrange
    collector = MappingCollector(MappingCollectorMode.FIRST)
    # Act
    collector.add('key1', 'value1')
    collector.add('key1', 'value2')
    # Assert
    assert collector.mapping['key1'] == 'value1'


# Adding duplicate keys in LAST mode
def test_adding_duplicate_keys_in_last_mode():
    # Arrange
    collector = MappingCollector(MappingCollectorMode.LAST)
    # Act
    collector.add('key1', 'value1')
    collector.add('key1', 'value2')
    # Assert
    assert collector.mapping['key1'] == 'value2'
