from mappingtools.transformers import strictify


def test_strictify_with_value_handler():
    # Arrange
    def value_handler(value):
        if isinstance(value, int):
            return value * 2
        return value

    data = {
        "a": 1,
        "b": "hello",
        "c": [2, 3],
        "d": {"e": 4},
    }

    expected = {
        "a": 2,
        "b": "hello",
        "c": [4, 6],
        "d": {"e": 8},
    }

    # Act
    result = strictify(data, value_handler=value_handler)

    # Assert
    assert result == expected


def test_strictify_with_string_iterable_and_value_handler():
    # Arrange
    def uppercase_handler(value):
        if isinstance(value, str):
            return value.upper()
        return value

    data = ["hello", "world", 123]
    expected = ["HELLO", "WORLD", 123]

    # Act
    result = strictify(data, value_handler=uppercase_handler)

    # Assert
    assert result == expected
