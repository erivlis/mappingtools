# Generated by CodiumAI

import pytest
from mappingtools import keep


class TestKeep:

    def test_keep_invalid_input(self):
        # Arrange
        keys = ['a', 'b']
        mapping = "invalid mapping"

        # Act & Assert
        with pytest.raises(TypeError):
            list(keep(keys, mapping))

    #  Keeps only specified keys from single mapping
    def test_keep_single_mapping(self):
        # Arrange
        keys = ['a', 'b']
        mapping = {'a': 1, 'b': 2, 'c': 3}

        # Act
        result = list(keep(keys, mapping))

        # Assert
        assert result == [{'a': 1, 'b': 2}]

    #  Keeps only specified keys from multiple mappings
    def test_keep_multiple_mappings(self):
        # Arrange
        keys = ['a', 'b']
        mappings = [{'a': 1, 'b': 2, 'c': 3}, {'a': 4, 'b': 5, 'd': 6}]

        # Act
        result = list(keep(keys, *mappings))

        # Assert
        assert result == [{'a': 1, 'b': 2}, {'a': 4, 'b': 5}]

    #  Handles empty keys list gracefully
    def test_keep_empty_keys(self):
        # Arrange
        keys = []
        mapping = {'a': 1, 'b': 2, 'c': 3}

        # Act
        result = list(keep(keys, mapping))

        # Assert
        assert result == [{}]

    #  Handles empty mappings gracefully
    def test_keep_empty_mappings(self):
        # Arrange
        keys = ['a', 'b']
        mappings = [{}]

        # Act
        result = list(keep(keys, *mappings))

        # Assert
        assert result == [{}]

    #  Works with different types of mappings
    def test_keep_different_mapping_types(self):
        # Arrange
        keys = ['a', 'b']
        mapping = {'a': 1, 'b': 2, 'c': 3}

        # Act
        result = list(keep(keys, mapping))

        # Assert
        assert result == [{'a': 1, 'b': 2}]

    #  Keys not present in any mapping
    def test_keep_keys_not_present(self):
        # Arrange
        keys = ['x', 'y']
        mapping = {'a': 1, 'b': 2, 'c': 3}

        # Act
        result = list(keep(keys, mapping))

        # Assert
        assert result == [{}]

    #  All keys present in all mappings
    def test_keep_all_keys_present(self):
        # Arrange
        keys = ['a', 'b']
        mappings = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]

        # Act
        result = list(keep(keys, *mappings))

        # Assert
        assert result == [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]

    #  Some keys present in some mappings
    def test_keep_some_keys_present(self):
        # Arrange
        keys = ['a', 'b']
        mappings = [{'a': 1, 'c': 3}, {'b': 2, 'd': 4}]

        # Act
        result = list(keep(keys, *mappings))

        # Assert
        assert result == [{'a': 1}, {'b': 2}]

    #  Duplicate keys in the input list
    def test_keep_duplicate_keys(self):
        # Arrange
        keys = ['a', 'a', 'b']
        mapping = {'a': 1, 'b': 2, 'c': 3}

        # Act
        result = list(keep(keys, mapping))

        # Assert
        assert result == [{'a': 1, 'b': 2}]

    #  Non-iterable keys input
    def test_keep_non_iterable_keys_input(self):
        # Arrange
        keys = None
        mapping = {'a': 1, 'b': 2}

        # Act and Assert
        with pytest.raises(TypeError):
            list(keep(keys, mapping))

    #  Handles large mappings efficiently
    def test_keep_large_mappings_efficiency(self):
        # Arrange
        keys = [f'key_{i}' for i in range(1000)]
        mapping = {f'key_{i}': i for i in range(1000)}

        # Act and Assert (no performance assertion here)
        result = list(keep(keys, mapping))

        assert len(result[0]) == len(keys)

    #  Works with nested mappings
    def test_keep_nested_mappings(self):
        # Arrange
        keys = ['a', 'b']
        mapping = {'a': {'nested_a': 1}, 'b': {'nested_b': 2}, 'c': {'nested_c': 3}}

        # Act
        result = list(keep(keys, mapping))

        # Assert
        assert result == [{'a': {'nested_a': 1}, 'b': {'nested_b': 2}}]
