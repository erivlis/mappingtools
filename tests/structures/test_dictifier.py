import contextlib

import pytest

from mappingtools.structures import Dictifier, dictify


class Address:
    def __init__(self, city: str):
        self.city = city

class Greeter:
    def __init__(self, greeting: str, city: str = "Nowhere"):
        self.greeting = greeting
        self.address = Address(city)

    def greet(self, name: str) -> str:
        return f"{self.greeting}, {name}!"

    def greet_untyped(self, name: str):
        return f"{self.greeting}, {name}!"

    def greet_forward_ref(self, name: str) -> "NonExistentClass":  # noqa: F821
        # This method's type hint cannot be resolved at runtime
        return f"{self.greeting}, {name}!"

    @property
    def greeting_length(self) -> int:
        return len(self.greeting)


class ExuberantGreeter(Greeter):
    def greet(self, name: str) -> str:
        return f"{self.greeting.upper()}!!! {name.upper()}!!!"

    def shout(self) -> str:
        return "YAAAS!"


class DepressedGreeter(Greeter):
    def greet(self, name: str) -> str:
        return f"...{self.greeting}... {name}..."


def test_dictifier_as_generic():
    """Test Dictifier used as a generic class."""
    # Arrange
    greeters = Dictifier[Greeter](
        {
            "english": Greeter("Hello"),
            "spanish": Greeter("Hola"),
        }
    )

    # Act
    greetings = greeters.greet("World")
    lengths = greeters.greeting_length

    # Assert
    assert isinstance(greetings, Dictifier)
    assert greetings._auto is False
    assert greetings == {
        "english": "Hello, World!",
        "spanish": "Hola, World!",
    }
    assert isinstance(lengths, dict)
    assert lengths == {"english": 5, "spanish": 4}


def test_dictifier_attribute_error():
    """Test that AttributeError is raised for missing attributes."""
    # Arrange
    greeters = Dictifier[Greeter]({"english": Greeter("Hello")})

    # Act & Assert
    with pytest.raises(AttributeError) as excinfo:
        greeters.non_existent_method()
    assert "'Greeter' object has no attribute 'non_existent_method'" in str(excinfo.value)

    with pytest.raises(AttributeError) as excinfo:
        greeters.non_existent_property
    assert "'Greeter' object has no attribute 'non_existent_property'" in str(excinfo.value)


def test_dictifier_empty():
    """Test behavior of an empty Dictifier."""
    # Arrange
    empty_greeters = Dictifier[Greeter]()

    # Act
    greetings = empty_greeters.greet("World")
    lengths = empty_greeters.greeting_length

    # Assert
    assert isinstance(greetings, Dictifier)
    assert greetings._auto is False
    assert not greetings
    assert isinstance(lengths, dict)
    assert not lengths


def test_dictifier_empty_no_type_raises_error():
    """Test that calling methods on an empty, non-typed Dictifier raises an error."""
    # Arrange
    empty_dict = Dictifier()

    # Act & Assert
    with pytest.raises(AttributeError) as excinfo:
        empty_dict.some_method()
    assert "It is empty and no wrapped type was specified" in str(excinfo.value)


def test_dictifier_no_inference():
    """Test that the standard Dictifier does NOT infer types."""
    # Arrange
    greeters = Dictifier(
        {
            "english": Greeter("Hello"),
            "spanish": Greeter("Hola"),
        }
    )

    # Act & Assert
    with pytest.raises(AttributeError) as excinfo:
        greeters.greet("Universe")
    assert "no wrapped type was specified" in str(excinfo.value)


def test_dictifier_generic_no_args():
    """Test Dictifier with __orig_class__ but no type arguments."""
    # Arrange
    d = Dictifier()
    # Manually set __orig_class__ to a type without args (like the raw Dictifier class)
    # This is needed to test a specific branch in _get_target_type
    with contextlib.suppress(AttributeError):
        d.__orig_class__ = Dictifier

    # Act & Assert
    with pytest.raises(AttributeError) as excinfo:
        d.some_method()
    assert "It is empty and no wrapped type was specified" in str(excinfo.value)


def test_dictifier_polymorphism():
    """Test that Dictifier handles subclasses correctly (polymorphism)."""
    # Arrange
    greeters = Dictifier[Greeter](
        {
            "normal": Greeter("Hello"),
            "exuberant": ExuberantGreeter("Hi"),
            "depressed": DepressedGreeter("Oh"),
        }
    )

    # Act
    greetings = greeters.greet("World")

    # Assert
    assert greetings == {
        "normal": "Hello, World!",
        "exuberant": "HI!!! WORLD!!!",
        "depressed": "...Oh... World...",
    }

    # Act & Assert for subclass-specific method
    with pytest.raises(AttributeError) as excinfo:
        greeters.shout()
    assert "'Greeter' object has no attribute 'shout'" in str(excinfo.value)


def test_dictifier_field_access():
    """Test accessing a simple instance variable (field) via Dictifier."""
    # Arrange
    greeters = Dictifier[Greeter]({
        "english": Greeter("Hello"),
        "spanish": Greeter("Hola"),
    })

    # Act
    greetings = greeters.greeting

    # Assert
    assert isinstance(greetings, dict)
    assert greetings == {
        "english": "Hello",
        "spanish": "Hola",
    }


def test_dictifier_chaining_with_type_hints():
    """Test chaining method calls when return types are hinted."""
    # Arrange
    greeters = Dictifier[Greeter]({
        "english": Greeter("Hello"),
        "spanish": Greeter("Hola"),
    })

    # Act
    greetings = greeters.greet("World")
    upper_greetings = greetings.upper()

    # Assert
    assert isinstance(greetings, Dictifier)
    assert greetings._auto is False
    assert isinstance(upper_greetings, Dictifier)
    assert upper_greetings._auto is True
    assert upper_greetings == {
        "english": "HELLO, WORLD!",
        "spanish": "HOLA, WORLD!",
    }


def test_dictifier_chaining_fallback_to_auto():
    """Test that chaining falls back to auto mode when hints are missing."""
    # Arrange
    greeters = Dictifier[Greeter]({
        "english": Greeter("Hello"),
        "spanish": Greeter("Hola"),
    })

    # Act
    untyped_greetings = greeters.greet_untyped("World")
    upper_greetings = untyped_greetings.upper()

    # Assert
    assert isinstance(untyped_greetings, Dictifier)
    assert untyped_greetings._auto is True
    assert upper_greetings == {
        "english": "HELLO, WORLD!",
        "spanish": "HOLA, WORLD!",
    }


def test_dictifier_unresolvable_type_hint_fallback():
    """Test that chaining falls back to auto mode for unresolvable hints."""
    # Arrange
    greeters = Dictifier[Greeter]({
        "english": Greeter("Hello"),
    })

    # Act
    result = greeters.greet_forward_ref("World")

    # Assert
    assert isinstance(result, Dictifier)
    assert result._auto is True
    assert result == {"english": "Hello, World!"}


def test_dictifier_deep_field_access_with_hints():
    """Test deep field access when type hints are present."""
    # Arrange
    class TypedGreeter(Greeter):
        address: Address  # Hinted field

    greeters = Dictifier[TypedGreeter]({
        "a": TypedGreeter("Hi", "New York"),
        "b": TypedGreeter("Ho", "London"),
    })

    # Act
    addresses = greeters.address
    cities = addresses.city

    # Assert
    assert isinstance(addresses, Dictifier)
    assert addresses._auto is False
    assert cities == {
        "a": "New York",
        "b": "London",
    }


def test_dictifier_field_access_broken_hint():
    """Test field access with a broken type hint falls back to auto mode."""
    # Arrange
    class BrokenGreeter(Greeter):
        # Hint points to non-existent class
        bad_field: "NonExistentClass"  # noqa: F821

        def __init__(self, greeting):
            super().__init__(greeting)
            self.bad_field = "Something"

    greeters = Dictifier[BrokenGreeter]({
        "a": BrokenGreeter("Hi"),
    })

    # Act
    result = greeters.bad_field

    # Assert
    assert isinstance(result, Dictifier)
    assert result._auto is True
    assert result == {"a": "Something"}
