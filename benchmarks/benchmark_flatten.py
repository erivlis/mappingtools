import random
import timeit

from mappingtools.operators import KeyFormat, flatten

# --- Data Generation Functions ---

# 1. Small, balanced tree
NESTED_DATA_SMALL = {
    "a": 1, "b": {"c": 2, "d": [3, 4, {"e": 5}]}, "f": "a_string",
    "g": [{"h": 6, "i": [7, 8]}, {"j": 9}], "k": None,
}

# 2. Wide tree (high breadth)
def generate_wide_tree(width: int) -> dict:
    return {f"key_{i}": {"value": i, "leaf": True} for i in range(width)}

NESTED_DATA_WIDE = generate_wide_tree(1000)

# 3. Deep tree (high depth)
def generate_deep_tree(depth: int, value) -> dict:
    if depth == 0:
        return {"leaf": value}
    return {"child": generate_deep_tree(depth - 1, value)}

NESTED_DATA_DEEP = generate_deep_tree(100, "leaf_value")

# 4. List-heavy tree
NESTED_DATA_LIST_HEAVY = {
    "list_simple": [1, 2, 3, 4, 5] * 10,
    "list_of_dicts": [{"id": i, "name": f"item_{i}"} for i in range(50)],
    "nested_lists": [
        [1, 2, [3, 4, [5]]],
        list(range(20)),
    ],
}

# 5. Large "enterprise" tree
def generate_large_enterprise_tree(nodes: int) -> dict:
    tree = {}
    for i in range(nodes):
        tree[f"node_{i}"] = {
            "id": i,
            "config": {"param_a": f"value_{i}", "param_b": i * 1.1, "features": {"f1": True, "f2": False}},
            "metadata": {"owner": "team_a", "timestamp": timeit.default_timer()},
            "data": [random.randint(0, 100) for _ in range(10)],
        }
    return tree

NESTED_DATA_LARGE = generate_large_enterprise_tree(500)


# --- Benchmark Runner ---

SCENARIOS = {
    "Small, Balanced": (NESTED_DATA_SMALL, 10000),
    "Wide (1,000 keys)": (NESTED_DATA_WIDE, 1000),
    "Deep (100 levels)": (NESTED_DATA_DEEP, 5000),
    "List-Heavy": (NESTED_DATA_LIST_HEAVY, 1000),
    "Large Enterprise (500 nodes)": (NESTED_DATA_LARGE, 100),
}

def run_all_benchmarks():
    """Runs and prints benchmark results for all scenarios."""
    print("--- Flatten KeyFormat Performance Benchmark ---")
    print("Comparing different KeyFormat options in `operators.flatten`\n")

    for name, (data, repetitions) in SCENARIOS.items():
        print(f"--- Scenario: {name} ({repetitions:,} repetitions) ---")
        run_single_benchmark(data, repetitions)

def run_single_benchmark(data: dict, repetitions: int):
    """Runs and prints results for a single data scenario across KeyFormats."""
    times = {}

    for kf in KeyFormat:
        try:
            times[kf.name] = timeit.timeit(
                lambda: flatten(data, key_format=kf),
                number=repetitions,
            )
        except Exception:
            times[kf.name] = float('nan')

    # --- Print Results ---
    for name, t in times.items():
        if t != t:  # Check for NaN
            print(f"{name:<20}: N/A (error or unsupported)")
        else:
            print(f"{name:<20}: {t:.6f} seconds")
    print()

if __name__ == "__main__":
    run_all_benchmarks()
