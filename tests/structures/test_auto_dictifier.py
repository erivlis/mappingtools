import pytest

from mappingtools.structures.dictifier import AutoDictifier, Dictifier


class Address:
    def __init__(self, city: str):
        self.city = city

class Greeter:
    def __init__(self, greeting: str, city: str = "Nowhere"):
        self.greeting = greeting
        self.address = Address(city)

    def greet(self, name: str) -> str:
        return f"{self.greeting}, {name}!"


class ExuberantGreeter(Greeter):
    def greet(self, name: str) -> str:
        return f"{self.greeting.upper()}!!! {name.upper()}!!!"

    def shout(self) -> str:
        return "YAAAS!"


def test_auto_dictifier_inferred_type():
    """Test that AutoDictifier can infer the type from its values if not explicitly typed."""
    # Create an AutoDictifier without a type hint, but with data
    greeters = AutoDictifier(
        {
            "english": Greeter("Hello"),
            "spanish": Greeter("Hola"),
        }
    )

    # It should be able to infer that the values are Greeters and allow method calls
    greetings = greeters.greet("Universe")
    assert isinstance(greetings, Dictifier)
    assert greetings == {
        "english": "Hello, Universe!",
        "spanish": "Hola, Universe!",
    }


def test_auto_dictifier_inference_risk():
    """Test the risk of inference with mixed subclasses using AutoDictifier."""
    # If we let it infer, it picks the type of the first item.

    # Case A: First item is the subclass with the extra method.
    # It infers 'ExuberantGreeter'. It allows 'shout', but fails on the others.
    risky_greeters = AutoDictifier(
        {
            "exuberant": ExuberantGreeter("Hi"),
            "normal": Greeter("Hello"),
        }
    )

    # It allows the call because ExuberantGreeter has 'shout'
    # But it fails at runtime when it hits the normal Greeter
    with pytest.raises(AttributeError) as excinfo:
        risky_greeters.shout()
    # The error comes from the item itself, not the Dictifier wrapper
    assert "'Greeter' object has no attribute 'shout'" in str(excinfo.value)

    # Case B: First item is the base class.
    # It infers 'Greeter'. It blocks 'shout' immediately.
    safe_greeters = AutoDictifier(
        {
            "normal": Greeter("Hello"),
            "exuberant": ExuberantGreeter("Hi"),
        }
    )
    with pytest.raises(AttributeError) as excinfo:
        safe_greeters.shout()
    # The error comes from the Dictifier wrapper
    assert "'Greeter' object has no attribute 'shout'" in str(excinfo.value)


def test_auto_dictifier_empty_no_type():
    """Test that AutoDictifier fails gracefully when empty and untyped."""
    empty_auto = AutoDictifier()

    # It cannot infer the type because it's empty
    with pytest.raises(AttributeError) as excinfo:
        empty_auto.some_method()

    assert "It is empty and no wrapped type was specified" in str(excinfo.value)


def test_auto_dictifier_deep_field_access_inference():
    """Test deep field access with AutoDictifier using inference."""
    greeters = AutoDictifier({
        "a": Greeter("Hi", "New York"),
        "b": Greeter("Ho", "London"),
    })

    # 1. Access .address -> Should return AutoDictifier because it infers the values are objects
    addresses = greeters.address
    assert isinstance(addresses, AutoDictifier)

    # 2. Access .city on the result -> Should work via inference!
    cities = addresses.city
    assert cities == {
        "a": "New York",
        "b": "London",
    }
