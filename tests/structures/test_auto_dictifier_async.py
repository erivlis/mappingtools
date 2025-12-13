import asyncio

import pytest

from mappingtools.structures import AutoDictifier, Dictifier


class AsyncGreeter:
    def __init__(self, name: str):
        self.name = name

    async def greet(self) -> str:
        await asyncio.sleep(0.01)
        return f"Hello, {self.name}!"

@pytest.mark.asyncio
async def test_auto_dictifier_async_method():
    """Test calling an async method on an AutoDictifier (inferred type)."""
    # No type hint provided
    greeters = AutoDictifier({
        "a": AsyncGreeter("Alice"),
        "b": AsyncGreeter("Bob"),
    })

    # This should infer AsyncGreeter, find the async method, and return a coroutine
    results = await greeters.greet()

    assert isinstance(results, Dictifier)
    # Since greet() has a return hint -> str, it should return a strict Dictifier
    assert not isinstance(results, AutoDictifier)
    assert results == {
        "a": "Hello, Alice!",
        "b": "Hello, Bob!",
    }

@pytest.mark.asyncio
async def test_auto_dictifier_async_chaining():
    """Test chaining after awaiting an async result from AutoDictifier."""
    greeters = AutoDictifier({
        "a": AsyncGreeter("Alice"),
    })

    # (await greeters.greet()) returns a Dictifier[str]
    # .upper() is then called on that result
    result = (await greeters.greet()).upper()

    assert result == {"a": "HELLO, ALICE!"}
