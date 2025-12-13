import asyncio

import pytest

from mappingtools.structures import AutoDictifier, Dictifier


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

    async def greet_broken_hint(self) -> "NonExistentClass":
        await asyncio.sleep(0.01)
        return f"Hello, {self.name}!"

@pytest.mark.asyncio
async def test_dictifier_async_method():
    """Test calling an async method on a Dictifier."""
    greeters = Dictifier[AsyncGreeter]({
        "a": AsyncGreeter("Alice"),
        "b": AsyncGreeter("Bob"),
    })

    # This should return a coroutine that resolves to a Dictifier
    # We await the proxy call itself
    results = await greeters.greet()

    assert isinstance(results, Dictifier)
    assert not isinstance(results, AutoDictifier)
    assert results == {
        "a": "Hello, Alice!",
        "b": "Hello, Bob!",
    }

@pytest.mark.asyncio
async def test_dictifier_async_method_untyped():
    """Test calling an untyped async method falls back to AutoDictifier."""
    greeters = Dictifier[AsyncGreeter]({
        "a": AsyncGreeter("Alice"),
        "b": AsyncGreeter("Bob"),
    })

    # Should return AutoDictifier because greet_untyped has no hint
    results = await greeters.greet_untyped()

    assert isinstance(results, AutoDictifier)
    assert results == {
        "a": "Hi, Alice!",
        "b": "Hi, Bob!",
    }

@pytest.mark.asyncio
async def test_dictifier_async_chaining():
    """Test chaining after awaiting an async result."""
    greeters = Dictifier[AsyncGreeter]({
        "a": AsyncGreeter("Alice"),
    })

    # (await greeters.greet()) returns a Dictifier[str]
    # .upper() is then called on that result
    result = (await greeters.greet()).upper()

    assert result == {"a": "HELLO, ALICE!"}

@pytest.mark.asyncio
async def test_dictifier_async_broken_hint():
    """Test calling an async method with a broken type hint falls back to AutoDictifier."""
    greeters = Dictifier[AsyncGreeter]({
        "a": AsyncGreeter("Alice"),
    })

    # Should return AutoDictifier because the hint is unresolvable
    results = await greeters.greet_broken_hint()

    assert isinstance(results, AutoDictifier)
    assert results == {
        "a": "Hello, Alice!",
    }
