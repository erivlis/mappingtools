import pytest

from mappingtools.structures import Dictifier, dictify
from mappingtools.structures.dictifier import AutoDictifier


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

    def greet_forward_ref(self, name: str) -> "NonExistentClass":
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
    greeters = Dictifier[Greeter](
        {
            "english": Greeter("Hello"),
            "spanish": Greeter("Hola"),
        }
    )

    # Test method call
    greetings = greeters.greet("World")
    assert isinstance(greetings, Dictifier)
    assert not isinstance(greetings, AutoDictifier)
    assert greetings == {
        "english": "Hello, World!",
        "spanish": "Hola, World!",
    }

    # Test property access
    lengths = greeters.greeting_length
    assert isinstance(lengths, dict)
    assert lengths == {"english": 5, "spanish": 4}


def test_dictifier_as_decorator():
    """Test Dictifier used as a class decorator."""

    @dictify
    class GreeterCollection:
        def __init__(self, greeting: str):
            self.greeting = greeting

        def greet(self, name: str) -> str:
            return f"{self.greeting}, {name}!"

        @property
        def greeting_length(self) -> int:
            return len(self.greeting)

    items = GreeterCollection(
        {
            "english": GreeterCollection.Item("Hello"),
            "french": GreeterCollection.Item("Bonjour"),
        }
    )

    # Test method call
    greetings = items.greet("Galaxy")
    assert isinstance(greetings, Dictifier)
    assert not isinstance(greetings, AutoDictifier)
    assert greetings == {
        "english": "Hello, Galaxy!",
        "french": "Bonjour, Galaxy!",
    }

    # Test property access
    lengths = items.greeting_length
    assert isinstance(lengths, dict)
    assert lengths == {"english": 5, "french": 7}

    # Test that the subclass is a subclass of Dictifier
    assert issubclass(GreeterCollection, Dictifier)


def test_dictifier_attribute_error():
    """Test that AttributeError is raised for missing attributes."""
    greeters = Dictifier[Greeter]({"english": Greeter("Hello")})

    with pytest.raises(AttributeError) as excinfo:
        greeters.non_existent_method()
    assert "'Greeter' object has no attribute 'non_existent_method'" in str(excinfo.value)

    with pytest.raises(AttributeError) as excinfo:
        greeters.non_existent_property
    assert "'Greeter' object has no attribute 'non_existent_property'" in str(excinfo.value)


def test_dictifier_empty():
    """Test behavior of an empty Dictifier."""
    empty_greeters = Dictifier[Greeter]()

    # Method call on empty dictifier should return an empty dictifier
    greetings = empty_greeters.greet("World")
    assert isinstance(greetings, Dictifier)
    assert not isinstance(greetings, AutoDictifier)
    assert not greetings

    # Property access on empty dictifier should return an empty dict
    lengths = empty_greeters.greeting_length
    assert isinstance(lengths, dict)
    assert not lengths


def test_dictifier_empty_no_type_raises_error():
    """Test that calling methods on an empty, non-typed Dictifier raises an error."""
    empty_dict = Dictifier()
    with pytest.raises(AttributeError) as excinfo:
        empty_dict.some_method()
    assert "It is empty and no wrapped type was specified" in str(excinfo.value)


def test_dictifier_no_inference():
    """Test that the standard Dictifier does NOT infer types."""
    # Create a standard Dictifier without a type hint, but with data
    greeters = Dictifier(
        {
            "english": Greeter("Hello"),
            "spanish": Greeter("Hola"),
        }
    )

    # It should NOT infer the type and should raise AttributeError
    with pytest.raises(AttributeError) as excinfo:
        greeters.greet("Universe")
    assert "no wrapped type was specified" in str(excinfo.value)


def test_dictifier_decorator_empty():
    """Test an empty Dictifier created with the decorator pattern."""

    @dictify
    class GreeterCollection:
        # Added return type hint to ensure strict Dictifier is returned
        def greet(self, name: str) -> str: ...

    # Create an empty collection
    items = GreeterCollection()
    assert len(items) == 0

    # Method call on empty dictifier should return an empty dictifier
    greetings = items.greet("No one")
    assert isinstance(greetings, Dictifier)
    assert not isinstance(greetings, AutoDictifier)
    assert not greetings


def test_dictifier_generic_no_args():
    """Test Dictifier with __orig_class__ but no type arguments."""
    d = Dictifier()
    # Manually set __orig_class__ to a type without args (like the raw Dictifier class)
    d.__orig_class__ = Dictifier

    # This should trigger the path where orig_class is found, but type_args is empty.
    # It should fall through and raise AttributeError because no type is found.
    with pytest.raises(AttributeError) as excinfo:
        d.some_method()
    assert "It is empty and no wrapped type was specified" in str(excinfo.value)


def test_dictifier_polymorphism():
    """Test that Dictifier handles subclasses correctly (polymorphism)."""
    greeters = Dictifier[Greeter](
        {
            "normal": Greeter("Hello"),
            "exuberant": ExuberantGreeter("Hi"),
            "depressed": DepressedGreeter("Oh"),
        }
    )

    # 1. Test that the base class method works for all subclasses
    greetings = greeters.greet("World")
    assert greetings == {
        "normal": "Hello, World!",
        "exuberant": "HI!!! WORLD!!!",
        "depressed": "...Oh... World...",
    }

    # 2. Test that we CANNOT call a subclass-specific method via the base class Dictifier
    # The Dictifier thinks it holds 'Greeter's, so it shouldn't allow 'shout'
    with pytest.raises(AttributeError) as excinfo:
        greeters.shout()
    assert "'Greeter' object has no attribute 'shout'" in str(excinfo.value)


def test_dictifier_field_access():
    """Test accessing a simple instance variable (field) via Dictifier."""
    greeters = Dictifier[Greeter]({
        "english": Greeter("Hello"),
        "spanish": Greeter("Hola"),
    })

    # Access the 'greeting' field directly
    greetings = greeters.greeting

    assert isinstance(greetings, dict)
    assert greetings == {
        "english": "Hello",
        "spanish": "Hola",
    }


def test_dictifier_chaining_with_type_hints():
    """Test chaining method calls when return types are hinted."""
    greeters = Dictifier[Greeter]({
        "english": Greeter("Hello"),
        "spanish": Greeter("Hola"),
    })

    # 1. Call greet() -> returns a strict Dictifier[str] because greet is hinted
    greetings = greeters.greet("World")
    assert isinstance(greetings, Dictifier)
    assert not isinstance(greetings, AutoDictifier)

    # 2. Call upper() on that result -> returns an AutoDictifier because str.upper is a built-in
    # and get_type_hints usually fails on built-ins.
    upper_greetings = greetings.upper()

    # The result is an AutoDictifier, but it works!
    assert isinstance(upper_greetings, AutoDictifier)
    assert upper_greetings == {
        "english": "HELLO, WORLD!",
        "spanish": "HOLA, WORLD!",
    }


def test_dictifier_chaining_fallback_to_auto():
    """Test that chaining falls back to AutoDictifier when hints are missing."""
    greeters = Dictifier[Greeter]({
        "english": Greeter("Hello"),
        "spanish": Greeter("Hola"),
    })

    # 1. Call greet_untyped() -> returns an AutoDictifier because the method has no hint
    untyped_greetings = greeters.greet_untyped("World")
    assert isinstance(untyped_greetings, AutoDictifier)

    # 2. Call upper() on that result, which works via inference
    upper_greetings = untyped_greetings.upper()
    assert upper_greetings == {
        "english": "HELLO, WORLD!",
        "spanish": "HOLA, WORLD!",
    }


def test_dictifier_unresolvable_type_hint_fallback():
    """Test that chaining falls back to AutoDictifier for unresolvable hints."""
    greeters = Dictifier[Greeter]({
        "english": Greeter("Hello"),
    })

    # greet_forward_ref has a return hint of "NonExistentClass"
    # get_type_hints will raise a NameError, triggering the except block.
    result = greeters.greet_forward_ref("World")

    # The result should be an AutoDictifier as a fallback.
    assert isinstance(result, AutoDictifier)
    assert result == {"english": "Hello, World!"}


def test_dictifier_deep_field_access_with_hints():
    """Test deep field access when type hints are present."""
    # We need a class with a hinted field
    class TypedGreeter(Greeter):
        address: Address  # Hinted field

    greeters = Dictifier[TypedGreeter]({
        "a": TypedGreeter("Hi", "New York"),
        "b": TypedGreeter("Ho", "London"),
    })

    # 1. Access .address -> Should return Dictifier[Address] because of the hint
    addresses = greeters.address
    assert isinstance(addresses, Dictifier)
    assert not isinstance(addresses, AutoDictifier)

    # 2. Access .city on the result -> Should work!
    cities = addresses.city
    assert cities == {
        "a": "New York",
        "b": "London",
    }


def test_dictifier_field_access_broken_hint():
    """Test field access with a broken type hint falls back to AutoDictifier."""
    class BrokenGreeter(Greeter):
        # Hint points to non-existent class
        bad_field: "NonExistentClass"

        def __init__(self, greeting):
            super().__init__(greeting)
            self.bad_field = "Something"

    greeters = Dictifier[BrokenGreeter]({
        "a": BrokenGreeter("Hi"),
    })

    # Accessing bad_field should trigger get_type_hints, fail, and fallback
    result = greeters.bad_field

    # Since it falls back to AutoDictifier, and the value is a string (primitive),
    # AutoDictifier will infer it as a string.
    # Wait, AutoDictifier logic for primitives:
    # If we access a field, we return AutoDictifier(results).
    # AutoDictifier.__init__ doesn't do anything special.
    # So we get an AutoDictifier wrapping strings.

    assert isinstance(result, AutoDictifier)
    assert result == {"a": "Something"}
