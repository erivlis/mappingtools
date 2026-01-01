from collections import Counter

from mappingtools.aggregation import Aggregation
from mappingtools.operators import rekey


def test_rekey_basic():
    # Arrange
    data = {1: "apple", 2: "banana"}

    # Act
    # Use value as key
    result = rekey(data, lambda k, v: v)

    # Assert
    assert result == {"apple": "apple", "banana": "banana"}


def test_rekey_collision_distinct():
    # Arrange
    data = {"a": 1, "b": 1, "c": 2}

    # Act
    # Rekey to the value itself
    result = rekey(data, lambda k, v: v, aggregation=Aggregation.DISTINCT)

    # Assert
    assert result == {1: {1}, 2: {2}}


def test_rekey_collision_count():
    # Arrange
    data = {"a": "apple", "b": "apple", "c": "banana"}

    # Act
    result = rekey(data, lambda k, v: v, aggregation=Aggregation.COUNT)

    # Assert
    assert result == {"apple": Counter({"apple": 2}), "banana": Counter({"banana": 1})}


def test_rekey_collision_sum():
    # Arrange
    data = {"a": 10, "b": 20, "c": 30}

    # Act
    # Rekey all to the same key
    result = rekey(data, lambda k, v: "total", aggregation=Aggregation.SUM)

    # Assert
    assert result == {"total": 60.0}


def test_rekey_empty_mapping():
    # Arrange
    data = {}

    # Act
    result = rekey(data, lambda k, v: k)

    # Assert
    assert result == {}
