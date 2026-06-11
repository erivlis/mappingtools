from dataclasses import dataclass

from mappingtools.transformers import modify


@dataclass
class SampleDataClass:
    x: int
    y: str


def test_modify_with_value_handler():
    # Arrange
    def value_handler(value):
        if isinstance(value, int):
            return value * 10
        return value

    data = {
        "a": 1,
        "b": "hello",
        "c": [2, 3, "world"],
        "d": {"e": 4},
        "f": SampleDataClass(x=5, y="test"),
    }

    expected = {
        "a": 10,
        "b": "hello",
        "c": [20, 30, "world"],
        "d": {"e": 40},
        "f": SampleDataClass(x=5, y="test"), # Class instances are treated as leaves, but not modified by this handler
    }

    # Act
    result = modify(data, value_handler=value_handler)

    # Assert
    assert result == expected


def test_modify_with_key_handler():
    # Arrange
    def key_handler(key):
        return key.upper()

    data = {
        "a": 1,
        "b": {"c": 2},
    }

    expected = {
        "A": 1,
        "B": {"C": 2},
    }

    # Act
    result = modify(data, key_handler=key_handler)

    # Assert
    assert result == expected


def test_modify_with_both_handlers():
    # Arrange
    def key_handler(key):
        return f"key_{key}"

    def value_handler(value):
        if isinstance(value, str):
            return f"value_{value}"
        return value

    data = {
        "a": "apple",
        "b": {"c": "cherry"},
        "d": [1, "durian"],
    }

    expected = {
        "key_a": "value_apple",
        "key_b": {"key_c": "value_cherry"},
        "key_d": [1, "value_durian"],
    }

    # Act
    result = modify(data, key_handler=key_handler, value_handler=value_handler)

    # Assert
    assert result == expected


def test_modify_handles_class_instances_as_leaves():
    # Arrange
    original_instance = SampleDataClass(x=1, y="original")
    modified_instance = SampleDataClass(x=99, y="modified")

    def class_handler(value):
        if isinstance(value, SampleDataClass):
            return modified_instance
        return value

    data = {
        "a": 1,
        "b": original_instance,
        "c": [original_instance],
    }

    expected = {
        "a": 1,
        "b": modified_instance,
        "c": [modified_instance],
    }

    # Act
    result = modify(data, value_handler=class_handler)

    # Assert
    assert result == expected


def test_modify_can_mutate_class_instance_in_place():
    # Arrange
    instance_to_mutate = SampleDataClass(x=1, y="original")

    def mutating_handler(value):
        if isinstance(value, SampleDataClass):
            value.y = "mutated"
        return value

    data = {
        "a": instance_to_mutate,
        "b": [instance_to_mutate],
    }

    # Act
    # The 'result' variable will be a new dictionary, but the instance inside it will be the same one we passed in.
    result = modify(data, value_handler=mutating_handler)

    # Assert
    # 1. Check that the 'y' attribute of the original instance has been changed.
    assert instance_to_mutate.y == "mutated"

    # 2. Check that the instance in the new dictionary is the *exact same object* as the original instance.
    assert result["a"] is instance_to_mutate
    assert result["b"][0] is instance_to_mutate
