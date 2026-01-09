import random
import string
import timeit
from collections import Counter, defaultdict
from collections.abc import Callable
from typing import Any

from mappingtools.collectors import CategoryCounter as NewCategoryCounter
from mappingtools.typing import Category


# --- Legacy Implementation (Optimized for Batch) ---
class LegacyCategoryCounter(dict[str, defaultdict[Category, Counter]]):
    def __init__(self):
        super().__init__()
        self.total = Counter()

    def update(self, data, **categories: Category | Callable[[Any], Category]):
        self.total.update(data)
        for category_name, category_value in categories.items():
            # If callable, it runs on the BATCH 'data' if it expects a list,
            # OR we might have to map it.
            # The original implementation assumed category_value(data) returned the key
            # for the whole batch if data was a single item, or...
            # Wait, the original implementation had a subtle ambiguity.
            # If category_value was a callable, it did: category_value = category_value(data)
            # This implies the callable takes the WHOLE data.

            # To make the benchmark fair for "Item-by-Item" comparison where category depends on item:
            # The legacy implementation actually required the user to pre-group or pass a key
            # that applied to the whole batch, OR it assumed 'data' was a single item?

            # Let's look at the original code:
            # category_value = category_value(data) if callable(category_value) else category_value
            # self[category_name][category_value].update(data)

            # This means the category is CONSTANT for the entire batch 'data'.
            # e.g. update(['a', 'b'], source='file1') -> source='file1' for both.

            # The NEW implementation does:
            # for item in data: self.add(item, **categories)
            # -> category_value = func(item)

            # These are DIFFERENT semantics if 'categories' contains a function!
            # Legacy: func(batch) -> category
            # New: func(item) -> category

            # To benchmark fairly, we must use a constant category (non-callable)
            # or a callable that returns a constant.

            # However, if we want to categorize items differently (e.g. by length),
            # The Legacy implementation couldn't do that in one pass!
            # You had to loop yourself:
            # for item in data: legacy.update([item], len=len(item))

            # So the "Performance Cliff" exists only if you are doing "Batch Update with Constant Category".
            # If you are doing "Item-dependent Category", the Legacy one forced you to loop anyway.

            # Let's benchmark the "Batch Update with Constant Category" scenario,
            # which is where the regression is expected.

            val = category_value(data) if callable(category_value) else category_value
            if category_name not in self:
                self[category_name] = defaultdict(Counter)
            self[category_name][val].update(data)


# --- Benchmark Setup ---


def generate_data(n=100_000):
    return [''.join(random.choices(string.ascii_lowercase, k=5)) for _ in range(n)]


def run_benchmark():
    data = generate_data(100_000)

    print(f'Benchmark: Processing {len(data)} items')
    print('-' * 60)

    # Scenario 1: Constant Category (e.g., source='batch_1')
    # This is where Legacy shines (O(1) python overhead for category, O(N) C loop for counting)
    print('\nScenario 1: Constant Category (Batch Update)')

    def run_legacy_constant():
        c = LegacyCategoryCounter()
        c.update(data, source='batch_1')

    def run_new_constant():
        c = NewCategoryCounter()
        # New implementation 'collect' iterates the list
        c.collect(data, source='batch_1')

    t_legacy = timeit.timeit(run_legacy_constant, number=10)
    t_new = timeit.timeit(run_new_constant, number=10)

    print(f'Legacy (Batch Optimized): {t_legacy:.4f}s')
    print(f'New (Item Loop):          {t_new:.4f}s')
    print(f'Ratio (New/Legacy):       {t_new / t_legacy:.2f}x slower')

    # Scenario 2: Item-Dependent Category (e.g., length of string)
    # Legacy requires manual loop. New handles it internally.
    print('\nScenario 2: Item-Dependent Category (Manual Loop vs Internal Loop)')

    def run_legacy_dynamic():
        c = LegacyCategoryCounter()
        # We must loop manually because Legacy assumes category applies to the whole 'data' arg
        for item in data:
            c.update(item, length=len)

    def run_new_dynamic():
        c = NewCategoryCounter()
        # New implementation handles callable per item
        c.collect(data, length=len)

    t_legacy_dyn = timeit.timeit(run_legacy_dynamic, number=5)
    t_new_dyn = timeit.timeit(run_new_dynamic, number=5)

    print(f'Legacy (Manual Loop):     {t_legacy_dyn:.4f}s')
    print(f'New (Internal Loop):      {t_new_dyn:.4f}s')
    print(f'Ratio (New/Legacy):       {t_new_dyn / t_legacy_dyn:.2f}x')


if __name__ == '__main__':
    run_benchmark()
