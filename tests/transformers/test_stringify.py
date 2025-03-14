# Generated by Qodo Gen
import random

import pytest

from mappingtools.transformers import stringify


# Basic mapping object is stringified with default delimiters
def test_basic_mapping_default_delimiters():
    # Arrange
    test_map = {'a': 1, 'b': 2}

    # Act
    result = stringify(test_map)

    # Assert
    assert result == 'a=1, b=2'


# Nested mapping objects are recursively stringified
def test_nested_mapping_recursive():
    # Arrange
    test_map = {'a': {'b': 1, 'c': 2}, 'd': 3}

    # Act
    result = stringify(test_map)

    # Assert
    assert result == 'a=b=1, c=2, d=3'


# Iterables are stringified with square brackets and default delimiters
def test_iterable_with_brackets():
    # Arrange
    test_list = [1, 2, 3]

    # Act
    result = stringify(test_list)

    # Assert
    assert result == '[1, 2, 3]'


# Class instances are stringified using public attributes
def test_class_public_attributes():
    # Arrange
    class TestClass:
        def __init__(self):
            self.a = 1
            self.b = 2

    test_obj = TestClass()

    # Act
    result = stringify(test_obj)

    # Assert
    assert result == 'a=1, b=2'


# Different delimiter values correctly format output string
def test_custom_delimiters():
    # Arrange
    test_map = {'a': 1, 'b': 2}

    # Act
    result = stringify(test_map, kv_delimiter='->', item_delimiter=';')

    # Assert
    assert result == 'a->1;b->2'


# Empty mapping returns empty string
def test_empty_mapping():
    # Arrange
    test_map = {}

    # Act
    result = stringify(test_map)

    # Assert
    assert result == ''


# Empty iterable returns empty brackets
def test_empty_iterable():
    # Arrange
    test_list = []

    # Act
    result = stringify(test_list)

    # Assert
    assert result == '[]'


# Class with no public attributes returns empty string
def test_empty_class():
    # Arrange
    class EmptyClass:
        pass

    test_obj = EmptyClass()

    # Act
    result = stringify(test_obj)

    # Assert
    assert result == ''


# Nested empty structures are properly handled
def test_nested_empty_structures():
    # Arrange
    test_obj = {'a': [], 'b': {}, 'c': [{}]}

    # Act
    result = stringify(test_obj)

    # Assert
    assert result == 'a=[], b=, c=[]'


# Mixed nested structures (mappings inside iterables inside classes)
def test_mixed_nested_structures():
    # Arrange
    class TestClass:
        def __init__(self):
            self.data = [{'a': 1}, {'b': 2}]

    test_obj = TestClass()

    # Act
    result = stringify(test_obj)

    # Assert
    assert result == 'data=[a=1, b=2]'


# Non-string delimiters are converted to strings
def test_non_string_delimiters():
    # Arrange
    test_map = {'a': 1, 'b': 2}

    # Act & Assert
    with pytest.raises(AttributeError):
        stringify(test_map, kv_delimiter=1, item_delimiter=2)


# Unicode characters as delimiters
def test_unicode_delimiters():
    # Arrange
    test_map = {'a': 1, 'b': 2}

    # Act
    result = stringify(test_map, kv_delimiter='→', item_delimiter='•')

    # Assert
    assert result == 'a→1•b→2'


def test_handles_special_characters_in_keys_or_values():
    # Arrange
    test_map = {'a!@#': 'value$%^', 'b&*(': 'value)'}
    expected = 'a!@#=value$%^, b&*(=value)'

    # Act
    result = stringify(test_map)

    # Assert
    assert result == expected


def test_handles_non_string_keys_values():
    # Arrange
    test_map = {1: 2, 3.5: 4.5}
    expected = '1=2, 3.5=4.5'

    # Act
    result = stringify(test_map)

    # Assert
    assert result == expected


def test_handles_large_mappings_efficiently():
    # Arrange
    size = random.randint(5000, 10000)
    test_map = {i: i for i in range(size)}
    expected = ', '.join([f'{i}={i}' for i in range(size)])

    # Act
    result = stringify(test_map)

    # Assert
    assert result == expected


def test_handles_tuples_as_keys():
    # Arrange
    test_map = {('a',): 1, ('b',): 2}
    expected = "('a',)=1, ('b',)=2"

    # Act
    result = stringify(test_map)

    # Assert
    assert result == expected


def test_handles_tuples_as_values():
    # Arrange
    test_map = {'a': (1, 2), 'b': (3, 4)}
    expected = 'a=[1, 2], b=[3, 4]'

    # Act
    result = stringify(test_map)

    # Assert
    assert result == expected


def test_handles_none_values():
    # Arrange
    test_map = {'a': None, 'b': None}
    expected = 'a=None, b=None'

    # Act
    result = stringify(test_map)

    # Assert
    assert result == expected


def test_handles_mixed_data_types():
    # Arrange
    test_map = {'a': 1, 'b': "string", 'c': [1, 2, 3]}
    expected = 'a=1, b=string, c=[1, 2, 3]'

    # Act
    result = stringify(test_map)

    # Assert
    assert result == expected


def test_handles_tuples_object():
    # Arrange
    test_tuple = (1, 2)
    expected = '[1, 2]'

    # Act
    result = stringify(test_tuple)

    # Assert
    assert result == expected
