import asyncio
import timeit

from mappingtools.structures import Dictifier, LazyDictifier, dictify


class Greeter:
    def __init__(self, i: int):
        self.i = i

    def greet(self) -> str:
        return f"Hello {self.i}"

    async def greet_async(self) -> str:
        # No sleep to measure pure overhead
        return f"Hello {self.i}"

@dictify
class GreeterCollection:
    def __init__(self, i: int):
        self.i = i

    def greet(self) -> str:
        return f"Hello {self.i}"

    async def greet_async(self) -> str:
        return f"Hello {self.i}"


def run_native_loop(items: dict[str, Greeter]):
    return {k: v.greet() for k, v in items.items()}


def run_dictifier_sync(items: Dictifier[Greeter]):
    return items.greet()


def run_autodictifier_sync(items: Dictifier):
    return items.greet()

def run_dictify_sync(items: GreeterCollection):
    return items.greet()

def run_lazy_dictifier_sync(items: LazyDictifier[Greeter]):
    # We must force execution to be fair
    return dict(items.greet())


async def run_native_async(items: dict[str, Greeter]):
    coros = [v.greet_async() for v in items.values()]
    results = await asyncio.gather(*coros)
    return dict(zip(items.keys(), results))


async def run_dictifier_async(items: Dictifier[Greeter]):
    await items.greet_async()


def benchmark(size: int, iterations: int = 1000):
    print(f"\n--- Benchmarking with {size} items ({iterations} iterations) ---")

    # Setup data
    data = {str(i): Greeter(i) for i in range(size)}
    dictifier = Dictifier[Greeter](data)
    autodictifier = Dictifier.auto(data)
    lazy_dictifier = LazyDictifier[Greeter](data)

    # For the decorated class, we need to instantiate the items with the correct type
    decorated_data = {str(i): GreeterCollection.Item(i) for i in range(size)}
    dictified = GreeterCollection(decorated_data)


    # 1. Native Loop
    t_native = timeit.timeit(lambda: run_native_loop(data), number=iterations)
    print(f"Native Loop:        {t_native:.4f}s")

    # 2. Dictifier (Sync, Generic) - Slow path via __getattr__
    t_dictifier = timeit.timeit(lambda: run_dictifier_sync(dictifier), number=iterations)
    overhead_sync = (t_dictifier - t_native) / t_native * 100
    print(f"Dictifier (Generic):  {t_dictifier:.4f}s (Overhead: {overhead_sync:.1f}%)")

    # 3. Dictifier (Auto) - Slow path via __getattr__
    t_auto = timeit.timeit(lambda: run_autodictifier_sync(autodictifier), number=iterations)
    overhead_auto = (t_auto - t_native) / t_native * 100
    print(f"Dictifier (Auto):     {t_auto:.4f}s (Overhead: {overhead_auto:.1f}%)")

    # 4. Dictify (Sync, Decorator) - Fast path with pre-compiled method
    t_dictify = timeit.timeit(lambda: run_dictify_sync(dictified), number=iterations)
    overhead_dictify = (t_dictify - t_native) / t_native * 100
    print(f"Dictify (Decorator):  {t_dictify:.4f}s (Overhead: {overhead_dictify:.1f}%)")

    # 5. LazyDictifier (Sync) - Lazy path
    t_lazy = timeit.timeit(lambda: run_lazy_dictifier_sync(lazy_dictifier), number=iterations)
    overhead_lazy = (t_lazy - t_native) / t_native * 100
    print(f"LazyDictifier:        {t_lazy:.4f}s (Overhead: {overhead_lazy:.1f}%)")


    # Async Benchmarks (run in a loop)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def async_wrapper(func, arg):
        start = timeit.default_timer()
        for _ in range(iterations):
            await func(arg)
        return timeit.default_timer() - start

    # 6. Native Async
    t_native_async = loop.run_until_complete(async_wrapper(run_native_async, data))
    print(f"Native Async:         {t_native_async:.4f}s")

    # 7. Dictifier (Async)
    t_dictifier_async = loop.run_until_complete(async_wrapper(run_dictifier_async, dictifier))
    overhead_async = (t_dictifier_async - t_native_async) / t_native_async * 100
    print(f"Dictifier (Async):    {t_dictifier_async:.4f}s (Overhead: {overhead_async:.1f}%)")

    loop.close()


if __name__ == "__main__":
    benchmark(size=10, iterations=10000)
    benchmark(size=100, iterations=1000)
    benchmark(size=1000, iterations=100)
