import pytest

from mappingtools.structures import Dictifier


class Greeter:
    def __init__(self, greeting: str):
        self.greeting = greeting

    def greet(self, name: str) -> str:
        return f"{self.greeting}, {name}!"


def test_dictifier_auto_inferred_type():
    """Test that Dictifier in auto mode can infer the type from its values."""
    # Arrange
    greeters = Dictifier.auto(
        {
            "english": Greeter("Hello"),
            "spanish": Greeter("Hola"),
        }
    )

    # Act
    greetings = greeters.greet("Universe")

    # Assert
    assert greetings == {
        "english": "Hello, Universe!",
        "spanish": "Hola, Universe!",
    }


def test_dictifier_auto_empty_no_type():
    """Test that Dictifier in auto mode fails gracefully when empty."""
    # Arrange
    empty_auto = Dictifier.auto({})

    # Act & Assert
    with pytest.raises(AttributeError) as excinfo:
        empty_auto.some_method()
    assert "It is empty and no wrapped type was specified" in str(excinfo.value)


def test_dictifier_auto_inference_risk():
    """Test the risk of auto-inference with mixed types."""
    # Arrange
    mixed_items = Dictifier.auto(
        {
            "greeter": Greeter("Hello"),
            "string": "I am not a Greeter",
        }
    )

    # Act & Assert
    with pytest.raises(AttributeError) as excinfo:
        mixed_items.greet("World")
    assert "'str' object has no attribute 'greet'" in str(excinfo.value)


def test_dictifier_auto_deep_field_access_inference():
    """Test deep field access with auto-inference."""
    # Arrange
    class Address:
        def __init__(self, city: str):
            self.city = city

    class User:
        def __init__(self, name: str, city: str):
            self.name = name
            self.address = Address(city)

    users = Dictifier.auto(
        {
            "u1": User("Alice", "New York"),
            "u2": User("Bob", "London"),
        }
    )

    # Act
    addresses = users.address
    cities = addresses.city

    # Assert
    assert addresses._auto is True
    assert cities == {
        "u1": "New York",
        "u2": "London",
    }
