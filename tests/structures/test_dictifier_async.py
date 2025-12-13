import asyncio

import pytest

from mappingtools.structures import Dictifier


class AsyncGreeter:
    def __init__(self, name: str):
        self.name = name

    async def greet(self) -> str:
        # Simulate some IO delay
        await asyncio.sleep(0.01)
        return f"Hello, {self.name}!"

    async def greet_untyped(self):
        await asyncio.sleep(0.01)
        return f"Hi, {self.name}!"

    async def greet_broken_hint(self) -> "NonExistentClass":  # noqa: F821
        await asyncio.sleep(0.01)
        return f"Hello, {self.name}!"

@pytest.mark.asyncio
async def test_dictifier_async_method():
    """Test calling an async method on a Dictifier."""
    # Arrange
    greeters = Dictifier[AsyncGreeter]({
        "a": AsyncGreeter("Alice"),
        "b": AsyncGreeter("Bob"),
    })

    # Act
    results = await greeters.greet()

    # Assert
    assert isinstance(results, Dictifier)
    assert results._auto is False
    assert results == {
        "a": "Hello, Alice!",
        "b": "Hello, Bob!",
    }

@pytest.mark.asyncio
async def test_dictifier_async_method_untyped():
    """Test calling an untyped async method falls back to auto mode."""
    # Arrange
    greeters = Dictifier[AsyncGreeter]({
        "a": AsyncGreeter("Alice"),
        "b": AsyncGreeter("Bob"),
    })

    # Act
    results = await greeters.greet_untyped()

    # Assert
    assert isinstance(results, Dictifier)
    assert results._auto is True
    assert results == {
        "a": "Hi, Alice!",
        "b": "Hi, Bob!",
    }

@pytest.mark.asyncio
async def test_dictifier_async_chaining():
    """Test chaining after awaiting an async result."""
    # Arrange
    greeters = Dictifier[AsyncGreeter]({
        "a": AsyncGreeter("Alice"),
    })

    # Act
    result = (await greeters.greet()).upper()

    # Assert
    assert result == {"a": "HELLO, ALICE!"}

@pytest.mark.asyncio
async def test_dictifier_async_broken_hint():
    """Test calling an async method with a broken type hint falls back to auto mode."""
    # Arrange
    greeters = Dictifier[AsyncGreeter]({
        "a": AsyncGreeter("Alice"),
    })

    # Act
    results = await greeters.greet_broken_hint()

    # Assert
    assert isinstance(results, Dictifier)
    assert results._auto is True
    assert results == {
        "a": "Hello, Alice!",
    }

@pytest.mark.asyncio
async def test_dictifier_auto_async_method():
    """Test calling an async method on a Dictifier in auto mode."""
    # Arrange
    greeters = Dictifier.auto({
        "a": AsyncGreeter("Alice"),
        "b": AsyncGreeter("Bob"),
    })

    # Act
    results = await greeters.greet()

    # Assert
    assert isinstance(results, Dictifier)
    assert results._auto is False # The result is strict because greet() is hinted
    assert results == {
        "a": "Hello, Alice!",
        "b": "Hello, Bob!",
    }
