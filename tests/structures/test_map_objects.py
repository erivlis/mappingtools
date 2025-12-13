from mappingtools.structures import (
    Dictifier,
    LazyDictifier,
    map_objects,
)


class Greeter:
    def __init__(self, name: str):
        self.name = name
        self.call_count = 0

    def greet(self) -> str:
        self.call_count += 1
        return f"Hello, {self.name}!"

def test_map_objects_returns_auto_dictifier_by_default():
    """Test that map_objects returns a Dictifier in auto mode by default."""
    # Arrange
    data = {"a": Greeter("Alice")}

    # Act
    result = map_objects(data)

    # Assert
    assert isinstance(result, Dictifier)
    assert result._auto is True
    assert result.greet()["a"] == "Hello, Alice!"

def test_map_objects_returns_strict_dictifier_with_hint():
    """Test that map_objects returns a strict Dictifier when a type hint is provided."""
    # Arrange
    data = {"a": Greeter("Alice")}

    # Act
    result = map_objects(data, type_hint=Greeter)

    # Assert
    assert isinstance(result, Dictifier)
    assert result._auto is False
    assert result.greet()["a"] == "Hello, Alice!"

def test_map_objects_returns_lazy_dictifier():
    """Test that map_objects returns a LazyDictifier when lazy=True."""
    # Arrange
    greeter = Greeter("Alice")
    data = {"a": greeter}

    # Act (Inference)
    result_lazy = map_objects(data, lazy=True)

    # Assert (Inference)
    assert isinstance(result_lazy, LazyDictifier)
    assert greeter.call_count == 0
    assert result_lazy.greet()["a"] == "Hello, Alice!"
    assert greeter.call_count == 1

    # Arrange (Hinted)
    greeter.call_count = 0

    # Act (Hinted)
    result_lazy_hinted = map_objects(data, lazy=True, type_hint=Greeter)

    # Assert (Hinted)
    assert isinstance(result_lazy_hinted, LazyDictifier)
    assert greeter.call_count == 0
    assert result_lazy_hinted.greet()["a"] == "Hello, Alice!"
    assert greeter.call_count == 1
