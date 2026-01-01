from mappingtools.aggregation import Aggregation
from mappingtools.operators import rename


def test_rename_with_mapping():
    # Arrange
    data = {"a": 1, "b": 2}
    mapper = {"a": "alpha"}

    # Act
    result = rename(data, mapper)

    # Assert
    assert result == {"alpha": 1, "b": 2}
    assert data == {"a": 1, "b": 2}  # Immutability check


def test_rename_with_callable():
    # Arrange
    data = {"a": 1, "b": 2}

    # Act
    result = rename(data, str.upper)

    # Assert
    assert result == {"A": 1, "B": 2}


def test_rename_collision_last():
    # Arrange
    data = {"a": 1, "b": 2}
    mapper = {"a": "target", "b": "target"}

    # Act
    result = rename(data, mapper, aggregation=Aggregation.LAST)

    # Assert
    assert result == {"target": 2}


def test_rename_collision_first():
    # Arrange
    data = {"a": 1, "b": 2}
    mapper = {"a": "target", "b": "target"}

    # Act
    result = rename(data, mapper, aggregation=Aggregation.FIRST)

    # Assert
    assert result == {"target": 1}


def test_rename_collision_all():
    # Arrange
    data = {"a": 1, "b": 2}
    mapper = {"a": "target", "b": "target"}

    # Act
    result = rename(data, mapper, aggregation=Aggregation.ALL)

    # Assert
    assert result == {"target": [1, 2]}


def test_rename_collision_max():
    # Arrange
    data = {"a": 10, "b": 20}
    mapper = {"a": "target", "b": "target"}

    # Act
    result = rename(data, mapper, aggregation=Aggregation.MAX)

    # Assert
    assert result == {"target": 20.0}


def test_rename_empty_mapping():
    # Arrange
    data = {}
    mapper = {"a": "b"}

    # Act
    result = rename(data, mapper)

    # Assert
    assert result == {}
