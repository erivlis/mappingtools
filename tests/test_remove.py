# Generated by CodiumAI
from mappingtools import remove


class TestRemove:

    #  Removing specified keys from a single mapping
    def test_remove_single_mapping(self):
        # Arrange
        keys = ['a']
        mapping = {'a': 1, 'b': 2}

        # Act
        result = list(remove(keys, mapping))

        # Assert
        assert result == [{'b': 2}]

    #  Removing specified keys from multiple mappings
    def test_remove_multiple_mappings(self):
        # Arrange
        keys = ['a']
        mappings = [{'a': 1, 'b': 2}, {'a': 3, 'c': 4}]

        # Act
        result = list(remove(keys, *mappings))

        # Assert
        assert result == [{'b': 2}, {'c': 4}]

    #  Handling empty mappings without errors
    def test_remove_empty_mappings(self):
        # Arrange
        keys = ['a']
        mappings = [{}]

        # Act
        result = list(remove(keys, *mappings))

        # Assert
        assert result == [{}]

    #  Handling mappings with no keys to remove
    def test_remove_no_keys_to_remove(self):
        # Arrange
        keys = []
        mapping = {'a': 1, 'b': 2}

        # Act
        result = list(remove(keys, mapping))

        # Assert
        assert result == [{'a': 1, 'b': 2}]

    #  Removing keys from mappings with nested structures
    def test_remove_nested_structures(self):
        # Arrange
        keys = ['a']
        mapping = {'a': {'nested': 1}, 'b': 2}

        # Act
        result = list(remove(keys, mapping))

        # Assert
        assert result == [{'b': 2}]

    #  Removing keys that do not exist in the mappings
    def test_remove_nonexistent_keys(self):
        # Arrange
        keys = ['x']
        mapping = {'a': 1, 'b': 2}

        # Act
        result = list(remove(keys, mapping))

        # Assert
        assert result == [{'a': 1, 'b': 2}]

    #  Handling mappings with mixed data types
    def test_remove_mixed_data_types(self):
        # Arrange
        keys = ['a']
        mapping = {'a': 1, 'b': 'string', 'c': [1, 2, 3]}

        # Act
        result = list(remove(keys, mapping))

        # Assert
        assert result == [{'b': 'string', 'c': [1, 2, 3]}]

    #  Removing keys from mappings with overlapping keys
    def test_remove_overlapping_keys(self):
        # Arrange
        keys = ['a', 'b']
        mappings = [{'a': 1, 'b': 2}, {'b': 3, 'c': 4}]

        # Act
        result = list(remove(keys, *mappings))

        # Assert
        assert result == [{}, {'c': 4}]

    #  Handling mappings with None values
    def test_remove_none_values(self):
        # Arrange
        keys = ['a']
        mapping = {'a': None, 'b': 2}

        # Act
        result = list(remove(keys, mapping))

        # Assert
        assert result == [{'b': 2}]

    #  Removing keys from mappings with special characters
    def test_remove_special_characters_keys(self):
        # Arrange
        keys = ['@key']
        mapping = {'@key': 1, 'normal_key': 2}

        # Act
        result = list(remove(keys, mapping))

        # Assert
        assert result == [{'normal_key': 2}]

    #  Removing keys from large mappings efficiently
    def test_remove_large_mappings_efficiently(self):
        # Arrange
        keys = ['key_to_remove']
        mapping = {f'key_{i}': i for i in range(1000)}
        mapping['key_to_remove'] = -1

        # Act
        result = list(remove(keys, mapping))

        # Assert
        assert all('key_to_remove' not in m for m in result)

    #  Handling mappings with immutable data types
    def test_remove_immutable_data_types(self):
        # Arrange
        keys = ['a']
        mapping = {'a': (1, 2), 'b': frozenset([3, 4])}

        # Act
        result = list(remove(keys, mapping))

        # Assert
        assert result == [{'b': frozenset([3, 4])}]
