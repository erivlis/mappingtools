# Generated by CodiumAI

from collections import OrderedDict, namedtuple

import pytest
from mappingtools import stream


# Converts mapping to namedtuples correctly
def test_converts_mapping_to_namedtuples_correctly():
    # Arrange
    TestTuple = namedtuple('TestTuple', ['key', 'value'])
    mapping = {'a': 1, 'b': 2}

    # Act
    result = list(stream(mapping, TestTuple))

    # Assert
    expected = [TestTuple('a', 1), TestTuple('b', 2)]
    assert result == expected


# Uses provided NamedTuple class for conversion
def test_uses_provided_namedtuple_class_for_conversion():
    # Arrange
    CustomTuple = namedtuple('CustomTuple', ['key', 'value'])
    mapping = {'x': 10, 'y': 20}

    # Act
    result = list(stream(mapping, CustomTuple))

    # Assert
    expected = [CustomTuple('x', 10), CustomTuple('y', 20)]
    assert result == expected


# Yields all items from the mapping
def test_yields_all_items_from_mapping():
    # Arrange
    TestTuple = namedtuple('TestTuple', ['key', 'value'])
    mapping = {'a': 1, 'b': 2, 'c': 3}

    # Act
    result = list(stream(mapping, TestTuple))

    # Assert
    assert len(result) == 3


# Handles mappings with multiple key-value pairs
def test_handles_multiple_key_value_pairs():
    # Arrange
    TestTuple = namedtuple('TestTuple', ['key', 'value'])
    mapping = {'a': 1, 'b': 2, 'c': 3, 'd': 4}

    # Act
    result = list(stream(mapping, TestTuple))

    # Assert
    expected = [TestTuple(k, v) for k, v in mapping.items()]
    assert result == expected


# Works with different types of mappings
def test_works_with_different_types_of_mappings():
    # Arrange
    TestTuple = namedtuple('TestTuple', ['key', 'value'])
    mapping = OrderedDict([('a', 1), ('b', 2)])

    # Act
    result = list(stream(mapping, TestTuple))

    # Assert
    expected = [TestTuple('a', 1), TestTuple('b', 2)]
    assert result == expected


# Empty mapping input
def test_empty_mapping_input():
    # Arrange
    TestTuple = namedtuple('TestTuple', ['key', 'value'])
    mapping = {}

    # Act
    result = list(stream(mapping, TestTuple))

    # Assert
    assert result == []


# Mapping with non-hashable keys
def test_mapping_with_non_hashable_keys():
    # Arrange
    TestTuple = namedtuple('TestTuple', ['key', 'value'])
    mapping = {('a',): 1, ('b',): 2}

    # Act
    result = list(stream(mapping, TestTuple))

    # Assert
    expected = [TestTuple(('a',), 1), TestTuple(('b',), 2)]
    assert result == expected


# Mapping with None values
def test_mapping_with_none_values():
    # Arrange
    TestTuple = namedtuple('TestTuple', ['key', 'value'])
    mapping = {'a': None, 'b': None}

    # Act
    result = list(stream(mapping, TestTuple))

    # Assert
    expected = [TestTuple('a', None), TestTuple('b', None)]
    assert result == expected


# NamedTuple with no fields
def test_namedtuple_with_no_fields():
    # Arrange
    EmptyTuple = namedtuple('EmptyTuple', [])
    mapping = {'a': 1}

    # Act and Assert (should raise TypeError)
    with pytest.raises(TypeError):
        list(stream(mapping, EmptyTuple))


# Mapping with mixed data types
def test_mapping_with_mixed_data_types():
    # Arrange
    MixedTypeTuple = namedtuple('MixedTypeTuple', ['key', 'value'])
    mapping = {'a': 1, 'b': "string", 'c': [1, 2, 3]}

    # Act
    result = list(stream(mapping, MixedTypeTuple))

    # Assert
    expected = [MixedTypeTuple('a', 1), MixedTypeTuple('b', "string"), MixedTypeTuple('c', [1, 2, 3])]
    assert result == expected


# Handles large mappings efficiently
def test_handles_large_mappings_efficiently():
    # Arrange
    LargeTuple = namedtuple('LargeTuple', ['key', 'value'])
    large_mapping = {i: i for i in range(10000)}

    # Act and Assert (ensure it does not raise any exceptions)

    result = list(stream(large_mapping, LargeTuple))
    assert len(result) == 10000
    assert all(isinstance(item, LargeTuple) for item in result)
    assert all(item.key == item.value for item in result)
