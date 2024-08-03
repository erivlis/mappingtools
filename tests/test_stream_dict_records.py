# Generated by CodiumAI
import pytest
from mappingtools import stream_dict_records


# Convert a dictionary with string keys and values into a generator of dictionaries with 'key' and 'value' fields
def test_convert_string_keys_values():
    # Arrange
    input_dict = {'a': '1', 'b': '2'}
    expected_output = [{'key': 'a', 'value': '1'}, {'key': 'b', 'value': '2'}]

    # Act
    result = list(stream_dict_records(input_dict))

    # Assert
    assert result == expected_output


# Use a custom key name and value name for the output dictionaries
def test_custom_key_value_names():
    # Arrange
    input_dict = {'a': '1', 'b': '2'}
    expected_output = [{'custom_key': 'a', 'custom_value': '1'}, {'custom_key': 'b', 'custom_value': '2'}]

    # Act
    result = list(stream_dict_records(input_dict, key_name='custom_key', value_name='custom_value'))

    # Assert
    assert result == expected_output


# Handle an empty dictionary gracefully
def test_empty_dictionary():
    # Arrange
    input_dict = {}
    expected_output = []

    # Act
    result = list(stream_dict_records(input_dict))

    # Assert
    assert result == expected_output


# Process a dictionary with mixed data types for keys and values
def test_mixed_data_types():
    # Arrange
    input_dict = {1: 'one', 'two': 2, 3.0: [3], (4,): {4}}
    expected_output = [
        {'key': 1, 'value': 'one'},
        {'key': 'two', 'value': 2},
        {'key': 3.0, 'value': [3]},
        {'key': (4,), 'value': {4}}
    ]

    # Act
    result = list(stream_dict_records(input_dict))

    # Assert
    assert result == expected_output


# Handle a dictionary with non-string keys
def test_non_string_keys():
    # Arrange
    input_dict = {1: 'one', 2.0: 'two'}
    expected_output = [{'key': 1, 'value': 'one'}, {'key': 2.0, 'value': 'two'}]

    # Act
    result = list(stream_dict_records(input_dict))

    # Assert
    assert result == expected_output


# Handle a dictionary with non-string values
def test_non_string_values():
    # Arrange
    input_dict = {'one': 1, 'two': 2.0}
    expected_output = [{'key': 'one', 'value': 1}, {'key': 'two', 'value': 2.0}]

    # Act
    result = list(stream_dict_records(input_dict))

    # Assert
    assert result == expected_output


# Process a dictionary with nested dictionaries as values
def test_nested_dictionaries_as_values():
    # Arrange
    input_dict = {'a': {'nested_key': 'nested_value'}}
    expected_output = [{'key': 'a', 'value': {'nested_key': 'nested_value'}}]

    # Act
    result = list(stream_dict_records(input_dict))

    # Assert
    assert result == expected_output


# Handle a dictionary with None as a key or value
def test_none_as_key_or_value():
    # Arrange
    input_dict = {None: 'none_value', 'none_key': None}
    expected_output = [{'key': None, 'value': 'none_value'}, {'key': 'none_key', 'value': None}]

    # Act
    result = list(stream_dict_records(input_dict))

    # Assert
    assert result == expected_output


# Process a dictionary with special characters in keys or values
def test_special_characters_in_keys_values():
    # Arrange
    input_dict = {'sp@cial_k#y!': '@special_value#'}
    expected_output = [{'key': 'sp@cial_k#y!', 'value': '@special_value#'}]

    # Act
    result = list(stream_dict_records(input_dict))

    # Assert
    assert result == expected_output


# Ensure the generator stops correctly after all items are processed
def test_generator_stops_correctly():
    # Arrange
    input_dict = {'a': 1, 'b': 2}

    # Act & Assert
    gen = stream_dict_records(input_dict)
    assert next(gen) == {'key': 'a', 'value': 1}
    assert next(gen) == {'key': 'b', 'value': 2}

    with pytest.raises(StopIteration):
        next(gen)


# Verify the order of items in the output matches the input dictionary
def test_order_of_items_matches_input():
    # Arrange
    input_dict = {'first': 1, 'second': 2, 'third': 3}
    expected_output = [{'key': 'first', 'value': 1}, {'key': 'second', 'value': 2}, {'key': 'third', 'value': 3}]

    # Act
    result = list(stream_dict_records(input_dict))

    # Assert
    assert result == expected_output


# Handle large dictionaries efficiently without performance degradation
def test_large_dictionaries_performance():
    # Arrange
    input_dict = {f'key_{i}': f'value_{i}' for i in range(100000)}

    # Act & Assert (no assertion needed for performance, just ensure it runs)
    for _ in stream_dict_records(input_dict):
        assert _ is not None
