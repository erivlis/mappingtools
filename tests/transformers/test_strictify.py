from mappingtools.transformers import strictify


def test_strictify_with_value_converter():
    # Arrange
    def value_converter(value):
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
    result = strictify(data, value_converter=value_converter)

    # Assert
    assert result == expected
