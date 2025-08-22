import dataclasses

from mappingtools.operators import stream


# stream function yields items from the mapping when item_factory is None
def test_yields_items_without_item_factory():
    # Arrange
    mapping = {'a': 1, 'b': 2}

    # Act
    result = list(stream(mapping))

    # Assert
    assert result == [('a', 1), ('b', 2)]


# stream function yields transformed items when item_factory is provided
def test_yields_transformed_items_with_item_factory():
    # Arrange
    mapping = {'a': 1, 'b': 2}

    def item_factory(k, v):
        return k, v * 2

    # Act
    result = list(stream(mapping, item_factory))

    # Assert
    assert result == [('a', 2), ('b', 4)]


# stream function works with different types of mappings (e.g., dict, defaultdict)
def test_works_with_different_mappings():
    # Arrange
    from collections import defaultdict
    mapping = defaultdict(int, {'a': 1, 'b': 2})

    # Act
    result = list(stream(mapping))

    # Assert
    assert result == [('a', 1), ('b', 2)]


# stream function handles empty mappings correctly
def test_handles_empty_mappings():
    # Arrange
    mapping = {}

    # Act
    result = list(stream(mapping))

    # Assert
    assert result == []


# stream function works with various item_factory functions
def test_works_with_various_item_factories():
    # Arrange
    mapping = {'a': 1, 'b': 2}

    def item_factory(k, v):
        return k.upper(), v + 10

    # Act
    result = list(stream(mapping, item_factory))

    # Assert
    assert result == [('A', 11), ('B', 12)]


# stream function handles mappings with non-hashable keys
def test_handles_non_hashable_keys():
    # Arrange
    mapping = {('a',): 1, ('b',): 2}

    # Act
    result = list(stream(mapping))

    # Assert
    assert result == [(('a',), 1), (('b',), 2)]


# stream function handles mappings with None values
def test_handles_none_values():
    # Arrange
    mapping = {'a': None, 'b': 2}

    # Act
    result = list(stream(mapping))

    # Assert
    assert result == [('a', None), ('b', 2)]


# stream function handles mappings with mixed data types
def test_handles_mixed_data_types():
    # Arrange
    mapping = {'a': 1, 'b': 'two', 'c': [3]}

    # Act
    result = list(stream(mapping))

    # Assert
    assert result == [('a', 1), ('b', 'two'), ('c', [3])]


# stream function handles large mappings efficiently
def test_handles_large_mappings_efficiently():
    # Arrange
    mapping = {i: i for i in range(1000000)}

    # Act & Assert
    for i, item in enumerate(stream(mapping)):
        assert item == (i, i)
        if i >= 10:
            break  # Only check the first few items for efficiency


# stream function handles mappings with special characters in keys or values
def test_handles_special_characters_in_keys_or_values():
    # Arrange
    mapping = {'a!@#': 'value$%^', 'b&*(': 'value)'}

    # Act
    result = list(stream(mapping))

    # Assert
    assert result == [('a!@#', 'value$%^'), ('b&*(', 'value)')]


# stream function handles mappings with nested structures
def test_handles_nested_structures():
    # Arrange
    mapping = {'a': {'nested': 1}, 'b': [2, 3]}

    # Act
    result = list(stream(mapping))

    # Assert
    assert result == [('a', {'nested': 1}), ('b', [2, 3])]


# stream function handles mappings with cyclic references
def test_handles_cyclic_references():
    # Arrange
    a = {}
    b = {'a': a}
    a['b'] = b

    mapping = {'a': a, 'b': b}

    # Act & Assert (checking for no infinite loop)
    result = list(stream(mapping))

    assert len(result) == 2
    assert ('a', a) in result
    assert ('b', b) in result


def test_handles_dataclass_factory():
    mapping = {'a': 1, 'b': 2}

    @dataclasses.dataclass
    class CustomDC:
        key: str
        value: int

    result = list(stream(mapping, CustomDC))

    assert result[0].key == 'a'
    assert result[0].value == 1
    assert result[1].key == 'b'
    assert result[1].value == 2
