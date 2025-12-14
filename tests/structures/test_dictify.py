import asyncio

import pytest

from mappingtools.structures import Dictifier, dictify


def test_dictify_decorator():
    """Test the @dictify decorator."""
    # Arrange
    @dictify
    class GreeterCollection:
        # Class attribute (should be ignored by proxy generation loop)
        IGNORED_ATTR = "I am ignored"

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

    # Act
    greetings = items.greet("Galaxy")
    lengths = items.greeting_length

    # Assert
    assert isinstance(greetings, Dictifier)
    assert greetings._auto is False
    assert greetings == {
        "english": "Hello, Galaxy!",
        "french": "Bonjour, Galaxy!",
    }
    assert isinstance(lengths, dict)
    assert lengths == {"english": 5, "french": 7}
    assert issubclass(GreeterCollection, Dictifier)


def test_dictify_decorator_empty():
    """Test an empty collection created with the @dictify decorator."""
    # Arrange
    @dictify
    class GreeterCollection:
        # Added return type hint to ensure strict Dictifier is returned
        def greet(self, name: str) -> str: ...

    items = GreeterCollection()

    # Act
    greetings = items.greet("No one")

    # Assert
    assert len(items) == 0
    assert isinstance(greetings, Dictifier)
    assert greetings._auto is False
    assert not greetings


@pytest.mark.asyncio
async def test_dictify_async_method():
    """Test @dictify with async methods."""
    # Arrange
    @dictify
    class AsyncGreeter:
        def __init__(self, name: str):
            self.name = name

        async def greet(self) -> str:
            await asyncio.sleep(0.01)
            return f"Hello, {self.name}!"

        # Untyped async method (covers fallback to auto mode)
        async def greet_untyped(self):
            await asyncio.sleep(0.01)
            return f"Hi, {self.name}!"

    greeters = AsyncGreeter({
        "a": AsyncGreeter.Item("Alice"),
        "b": AsyncGreeter.Item("Bob"),
    })

    # Act
    results = await greeters.greet()
    results_untyped = await greeters.greet_untyped()

    # Assert
    assert isinstance(results, Dictifier)
    assert results._auto is False
    assert results == {"a": "Hello, Alice!", "b": "Hello, Bob!"}
    assert isinstance(results_untyped, Dictifier)
    assert results_untyped._auto is True
    assert results_untyped == {"a": "Hi, Alice!", "b": "Hi, Bob!"}


def test_dictify_deep_proxy():
    """Test @dictify with deep proxying (fields/properties)."""
    # Arrange
    class Address:
        def __init__(self, city):
            self.city = city

    @dictify
    class User:
        address: Address  # Field hint
        _private: Address # Private field hint (should be ignored)

        def __init__(self, name, city):
            self.name = name
            self.address = Address(city)
            self._private = Address("Secret")

        @property
        def prop_address(self) -> Address: # Property hint
            return self.address

    users = User({
        "u1": User.Item("Alice", "NY"),
    })

    # Act
    addresses = users.address
    prop_addresses = users.prop_address

    # Assert
    assert isinstance(addresses, Dictifier)
    assert addresses._auto is False
    assert addresses.city == {"u1": "NY"}
    assert isinstance(prop_addresses, Dictifier)
    assert prop_addresses.city == {"u1": "NY"}


def test_dictify_broken_hints():
    """Test @dictify with broken type hints (should fallback gracefully)."""
    # Arrange
    @dictify
    class Broken:
        bad_field: "NonExistent"  # noqa: F821

        def __init__(self, val):
            self.bad_field = val

        def bad_method(self) -> "NonExistent":  # noqa: F821
            return self.bad_field

        @property
        def bad_prop(self) -> "NonExistent":  # noqa: F821
            return self.bad_field

    items = Broken({"a": Broken.Item("test")})

    # Act
    field_result = items.bad_field
    method_result = items.bad_method()
    prop_result = items.bad_prop

    # Assert
    assert isinstance(field_result, Dictifier)
    assert field_result._auto is True
    assert isinstance(method_result, Dictifier)
    assert method_result._auto is True
    assert isinstance(prop_result, Dictifier)
    assert prop_result._auto is True


def test_dictify_class_with_unresolvable_hints():
    """Test that @dictify does not crash on a class where get_type_hints fails."""
    # Arrange
    try:
        # This class will cause get_type_hints to raise a NameError
        @dictify
        class BrokenClass:
            x: "SomeNonExistentType" = "Value" # noqa: F821

            def greet(self) -> str:
                return "Hello"

        # Act
        items = BrokenClass({"a": BrokenClass.Item()})

        # 1. Method call should still work and be strict (because method hint is valid)
        greet_result = items.greet()
        assert isinstance(greet_result, Dictifier)
        assert greet_result._auto is False
        assert greet_result == {"a": "Hello"}

        # 2. Field access should fall back to auto (because class hint fails)
        field_result = items.x
        assert isinstance(field_result, Dictifier)
        assert field_result._auto is True
        assert field_result == {"a": "Value"}

    except NameError:
        pytest.fail("dictify should not raise NameError on unresolvable type hints")


def test_dictify_validation_error():
    """Test that @dictify raises TypeError if applied to a non-class."""
    # Act & Assert
    with pytest.raises(TypeError) as excinfo:
        dictify("not a class")

    assert "Dictifier.of() expects a class" in str(excinfo.value)
