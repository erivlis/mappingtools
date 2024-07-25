# Generated by CodiumAI
import dataclasses

from mappingtools import unwrap


#  Unwraps a dictionary into a list of key-value pairs
def test_unwrap_dictionary():
    # Arrange
    obj = {'a': 1, 'b': 2}
    expected = [{'key': 'a', 'value': 1}, {'key': 'b', 'value': 2}]

    # Act
    result = unwrap(obj)

    # Assert
    assert result == expected


#  Unwraps a list into a list of unwrapped elements
def test_unwrap_list():
    # Arrange
    obj = [1, 2, 3]
    expected = [1, 2, 3]

    # Act
    result = unwrap(obj)

    # Assert
    assert result == expected


#  Unwraps a dataclass into a list of key-value pairs
def test_unwrap_dataclass():
    # Arrange
    @dataclasses.dataclass
    class TestClass:
        x: int
        y: int

    obj = TestClass(1, 2)
    expected = [{'key': 'x', 'value': 1}, {'key': 'y', 'value': 2}]

    # Act
    result = unwrap(obj)

    # Assert
    assert result == expected


#  Returns the original object if it is not a mapping, iterable, or dataclass
def test_unwrap_non_mapping_iterable_dataclass():
    # Arrange
    obj = 42

    # Act
    result = unwrap(obj)

    # Assert
    assert result == obj


#  Correctly handles nested structures by recursively unwrapping
def test_unwrap_nested_structures():
    # Arrange
    obj = {'a': [1, {'b': 2}]}
    expected = [{'key': 'a', 'value': [1, [{'key': 'b', 'value': 2}]]}]

    # Act
    result = unwrap(obj)

    # Assert
    assert result == expected


#  Handles empty dictionaries and lists without errors
def test_unwrap_empty_structures():
    # Arrange
    empty_dict = {}
    empty_list = []

    # Act & Assert
    assert unwrap(empty_dict) == []
    assert unwrap(empty_list) == []


#  Handles objects with mixed types (e.g., lists containing dictionaries)
def test_unwrap_mixed_types():
    # Arrange
    obj = [{'a': 1}, [2, {'b': 3}]]
    expected = [[{'key': 'a', 'value': 1}], [2, [{'key': 'b', 'value': 3}]]]

    # Act
    result = unwrap(obj)

    # Assert
    assert result == expected


#  Processes objects with non-string keys and values
def test_unwrap_non_string_keys_values():
    # Arrange
    obj = {1: 2, 3.5: 4.5}
    expected = [{'key': 1, 'value': 2}, {'key': 3.5, 'value': 4.5}]

    # Act
    result = unwrap(obj)

    # Assert
    assert result == expected


#  Handles objects with circular references gracefully
# def test_unwrap_circular_references():
#     # Arrange
#     obj = {}
#     obj['self'] = obj
#
#     # Act & Assert (should not raise an error)
#     try:
#         unwrap(obj)
#         assert True
#     except RecursionError:
#         assert False, "RecursionError was raised"

#  Processes objects with deeply nested structures
def test_unwrap_deeply_nested_structures():
    # Arrange
    obj = {'a': {'b': {'c': {'d': 1}}}}
    expected = [{'key': 'a', 'value': [{'key': 'b', 'value': [{'key': 'c', 'value': [{'key': 'd', 'value': 1}]}]}]}]

    # Act
    result = unwrap(obj)

    # Assert
    assert result == expected


#  Handles custom objects that are not dataclasses
def test_unwrap_custom_objects_not_dataclasses():
    # Arrange
    class CustomClass:
        def __init__(self, value):
            self.value = value

    obj = CustomClass(10)

    expected = [{'key': 'value', 'value': 10}]

    # Act (should return the string representation of the object)
    actual = unwrap(obj)

    # Assert
    assert actual == expected


#  Processes objects with special characters in keys or values
def test_unwrap_special_characters_in_keys_values():
    # Arrange
    obj = {'sp￯﾿ﾃ￯ﾾﾩcial_k￯﾿ﾃ￯ﾾﾩy!@#': 'v￯﾿ﾃ￯ﾾﾤlue$%^'}
    expected = [{'key': 'sp￯﾿ﾃ￯ﾾﾩcial_k￯﾿ﾃ￯ﾾﾩy!@#', 'value': 'v￯﾿ﾃ￯ﾾﾤlue$%^'}]

    # Act
    result = unwrap(obj)

    # Assert
    assert result == expected
