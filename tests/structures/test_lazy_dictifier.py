from collections.abc import Mapping

import pytest

from mappingtools.structures import Dictifier, LazyDictifier


class Greeter:
    def __init__(self, name: str):
        self.name = name
        self.call_count = 0

    def greet(self) -> str:
        self.call_count += 1
        return f"Hello, {self.name}!"

    @property
    def name_len(self) -> int:
        return len(self.name)

def test_lazy_dictifier_is_mapping():
    """Test that LazyDictifier implements the Mapping interface."""
    data = {"a": 1}
    lazy = LazyDictifier(data)
    assert isinstance(lazy, Mapping)
    assert len(lazy) == 1
    assert list(lazy) == ["a"]
    assert repr(lazy) == "LazyDictifier(source={'a': 1}, ops=0)"

def test_lazy_dictifier_execution_is_lazy():
    """Test that methods are not called until item access."""
    greeter = Greeter("Alice")
    data = {"a": greeter}
    lazy = LazyDictifier(data)

    # Create the proxy - should NOT call greet() yet
    greetings = lazy.greet()
    assert greeter.call_count == 0
    assert isinstance(greetings, LazyDictifier)

    # Access an item - SHOULD call greet() now
    assert greetings["a"] == "Hello, Alice!"
    assert greeter.call_count == 1

def test_lazy_dictifier_chaining():
    """Test chaining multiple lazy operations."""
    greeter = Greeter("Bob")
    data = {"b": greeter}
    lazy = LazyDictifier(data)

    # Chain: greet() -> upper()
    # greet() returns str, upper() is on str
    pipeline = lazy.greet().upper()

    assert greeter.call_count == 0

    # Execute
    assert pipeline["b"] == "HELLO, BOB!"
    assert greeter.call_count == 1

def test_lazy_dictifier_field_access():
    """Test lazy access to fields/properties."""
    data = {"c": Greeter("Charlie")}
    lazy = LazyDictifier(data)

    # Access property
    lengths = lazy.name_len
    assert isinstance(lengths, LazyDictifier)

    assert lengths["c"] == 7 # "Charlie"

def test_lazy_dictifier_inference():
    """Test that LazyDictifier infers type if not provided."""
    data = {"d": Greeter("Dave")}
    # No type hint
    lazy = LazyDictifier(data)

    # Should infer Greeter and allow greet()
    greetings = lazy.greet()
    assert greetings["d"] == "Hello, Dave!"

def test_lazy_dictifier_conversion():
    """Test converting LazyDictifier to a real dict."""
    data = {"e": Greeter("Eve")}
    lazy = LazyDictifier(data)

    # Convert to dict triggers execution for all items
    result = dict(lazy.greet())
    assert result == {"e": "Hello, Eve!"}

def test_lazy_dictifier_key_error():
    """Test that accessing a non-existent key raises KeyError."""
    lazy = LazyDictifier({"a": 1})
    with pytest.raises(KeyError):
        _ = lazy["b"]

def test_lazy_dictifier_empty_source():
    """Test behavior with an empty source."""
    lazy = LazyDictifier({})
    assert len(lazy) == 0
    assert list(lazy) == []
    assert lazy._get_target_type() is None

    # Accessing should still raise KeyError
    with pytest.raises(KeyError):
        _ = lazy.some_method()["a"]

def test_lazy_dictifier_inherits_type_from_dictifier():
    """Test that LazyDictifier can inherit its type from a Dictifier source."""
    greeters = Dictifier[Greeter]({"a": Greeter("Alice")})
    lazy = LazyDictifier(greeters)

    # It should know the type is Greeter without inference
    assert lazy._get_target_type() is Greeter

def test_lazy_dictifier_chaining_from_dictifier():
    """Test chaining on a LazyDictifier created from a Dictifier source."""
    greeters = Dictifier[Greeter]({"a": Greeter("Alice")})
    lazy = LazyDictifier(greeters)

    # This triggers __getattr__ -> _get_target_type -> hasattr(source, ...)
    greetings = lazy.greet()
    assert greetings["a"] == "Hello, Alice!"
