import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest

from mappingtools.structures import Dictifier


class GeneratorGreeter:
    def __init__(self, name: str):
        self.name = name

    def count_sync(self) -> Generator[int, None, None]:
        yield 1
        yield 2
        yield 3

    async def count_async(self) -> AsyncGenerator[int, None]:
        yield 1
        await asyncio.sleep(0.01)
        yield 2
        yield 3

def test_dictifier_sync_generator():
    """Test that Dictifier returns generator objects for generator methods."""
    greeters = Dictifier[GeneratorGreeter]({
        "a": GeneratorGreeter("Alice"),
        "b": GeneratorGreeter("Bob"),
    })

    # Call the generator method
    # This should return a Dictifier where values are generators
    results = greeters.count_sync()

    assert isinstance(results, Dictifier)
    # Since Generator is a class, it wraps it in Dictifier (strict)

    gen_a = results["a"]
    gen_b = results["b"]

    # Verify they are generators
    assert hasattr(gen_a, "__next__")
    assert hasattr(gen_b, "__next__")

    # Consume them
    assert list(gen_a) == [1, 2, 3]
    assert list(gen_b) == [1, 2, 3]

@pytest.mark.asyncio
async def test_dictifier_async_generator():
    """Test that Dictifier returns async generator objects for async generator methods."""
    greeters = Dictifier[GeneratorGreeter]({
        "a": GeneratorGreeter("Alice"),
        "b": GeneratorGreeter("Bob"),
    })

    # Call the async generator method
    # Note: We do NOT await the call itself because calling an async generator function
    # returns an async generator object immediately (it's not a coroutine).
    # However, our proxy might try to await it if it detects `async def`.

    # Wait! inspect.iscoroutinefunction() returns False for async generators!
    # It returns True for `async def foo(): return`.
    # It returns False for `async def foo(): yield`.
    # Instead, inspect.isasyncgenfunction() returns True.

    # Our current code uses `inspect.iscoroutinefunction(attr)`.
    # So it will fall through to `callable(attr)`.
    # It will execute `attr(*args)` synchronously.
    # This returns an async_generator object.

    results = greeters.count_async()

    assert isinstance(results, Dictifier)

    agen_a = results["a"]
    agen_b = results["b"]

    # Verify they are async generators
    assert hasattr(agen_a, "__aiter__")

    # Consume them
    vals_a = [i async for i in agen_a]
    vals_b = [i async for i in agen_b]

    assert vals_a == [1, 2, 3]
    assert vals_b == [1, 2, 3]
