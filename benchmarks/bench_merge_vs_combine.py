import random
import string
import timeit

from mappingtools.operators import combine, merge
from mappingtools.resolvers import Resolver

# --- Setup Small Data ---
base_tree_small = {
    "system": {
        "metadata": {"version": "1.0.0", "env": "prod"},
        "networking": {
            "ports": [80, 443, 8080],
            "firewall": {"enabled": True, "rules": ["allow_all"]}
        }
    },
    "users": {
        "admin": {"id": 1, "roles": ["super", "admin"]},
        "guest": {"id": 2, "roles": ["view_only"]}
    },
    "flags": {"feature_x": False, "feature_y": True}
}

override_tree_small = {
    "system": {
        "metadata": {"version": "1.0.1"},
        "networking": {
            "ports": [9000],
            "firewall": {"rules": ["deny_all"]}
        }
    },
    "users": {
        "guest": {"roles": ["editor"]}
    },
    "flags": {"feature_x": True, "feature_z": True}
}


# --- Setup Wide Data (Breadth) ---
def generate_wide_tree(width: int, prefix: str) -> dict:
    """Generates a shallow but wide dictionary."""
    return {f"key_{prefix}_{i}": {"value": i} for i in range(width)}


base_tree_wide = generate_wide_tree(1000, "base")
override_tree_wide = generate_wide_tree(1000, "override")
# Add some overlapping keys to force collisions
for i in range(200):
    override_tree_wide[f"key_base_{i}"] = {"value": i * 2, "overridden": True}


# --- Setup Deep Data (Depth) ---
def generate_deep_tree(depth: int, value) -> dict:
    """Generates a deeply nested dictionary."""
    if depth == 0:
        return {"leaf": value}
    return {"child": generate_deep_tree(depth - 1, value)}


base_tree_deep = generate_deep_tree(100, "base_value")
override_tree_deep = generate_deep_tree(100, "override_value")

# --- Setup List-Heavy Data ---
base_tree_list = {
    "list_simple": [1, 2, 3],
    "list_of_dicts": [
        {"id": 1, "name": "apple"},
        {"id": 2, "name": "banana"}
    ],
    "scalar_to_list": "a string",
    "mixed_list": [1, "hello", {"a": 1}]
}
override_tree_list = {
    "list_simple": [4, 5],
    "list_of_dicts": [
        {"id": 3, "name": "cherry"}
    ],
    "scalar_to_list": ["new", "list"],
    "list_to_scalar": "just a scalar now",
    "new_list": ["one", "two"]
}

# --- Setup Very Large Enterprise Data ---
def generate_large_enterprise_tree(nodes: int, prefix: str) -> dict:
    """Generates a very large, moderately deep tree simulating an enterprise payload."""
    tree = {}
    for i in range(nodes):
        tree[f"node_{prefix}_{i}"] = {
            "id": i,
            "config": {
                "param_a": f"value_{i}",
                "param_b": i * 1.1,
                "features": {"f1": True, "f2": False, "f3": i % 2 == 0}
            },
            "metadata": {"owner": f"team_{prefix}", "timestamp": timeit.default_timer()},
            "data": [random.randint(0, 100) for _ in range(10)]
        }
    return tree

base_tree_large = generate_large_enterprise_tree(2000, "base")
override_tree_large = generate_large_enterprise_tree(500, "override")
# Add some deep overrides
override_tree_large["node_base_10"] = {"config": {"features": {"f2": True, "f4": True}}}


# --- Setup Skewed Tree Data ---
def generate_skewed_tree(deep_levels: int, wide_nodes: int, prefix: str) -> dict:
    """Generates a tree with one very deep branch and several wide, shallow branches."""
    tree = generate_wide_tree(wide_nodes, f"{prefix}_wide")
    # Create a single, very deep branch
    deep_branch = tree
    for i in range(deep_levels):
        key = f"deep_{prefix}_{i}"
        deep_branch[key] = {}
        deep_branch = deep_branch[key]
    deep_branch["leaf"] = f"{prefix}_leaf_value"
    return tree

base_tree_skewed = generate_skewed_tree(100, 100, "base")
override_tree_skewed = generate_skewed_tree(50, 100, "override")
# Override a key in the wide part and a key deep in the base branch
override_tree_skewed["key_base_wide_5"] = {"value": "overridden"}
override_tree_skewed["deep_base_90"] = {"new_leaf": "deep_override"}


# --- Setup Stochastic Tree Data ---
def _generate_random_value(depth: int):
    if depth <= 0:
        return random.choice([
            ''.join(random.choices(string.ascii_lowercase, k=5)),
            random.randint(0, 1000),
            random.random(),
            True,
            None
        ])
    
    val_type = random.choice(['dict', 'list', 'primitive'])
    if val_type == 'dict':
        return {
            ''.join(random.choices(string.ascii_lowercase, k=5)): _generate_random_value(depth - 1)
            for _ in range(random.randint(1, 5))
        }
    elif val_type == 'list':
        return [_generate_random_value(depth - 1) for _ in range(random.randint(1, 5))]
    else:
        return _generate_random_value(0)

def generate_stochastic_tree(max_depth: int, num_keys: int, collision_rate: float) -> tuple[dict, dict]:
    """Generates two trees with random structure, types, and controlled collisions."""
    base = {f"key_{i}": _generate_random_value(random.randint(1, max_depth)) for i in range(num_keys)}
    override = {}
    
    base_keys = list(base.keys())
    for i in range(int(num_keys * collision_rate)):
        key_to_override = random.choice(base_keys)
        override[key_to_override] = _generate_random_value(random.randint(1, max_depth))
        
    # Add some new keys to the override tree
    for i in range(int(num_keys * 0.2)):
        override[f"new_key_{i}"] = _generate_random_value(random.randint(1, max_depth))
        
    return base, override

base_tree_stochastic, override_tree_stochastic = generate_stochastic_tree(max_depth=5, num_keys=100, collision_rate=0.5)


def run_benchmark(name: str, base: dict, override: dict, iterations: int):
    print(f"\n--- Benchmarking: {name} ({iterations:,} iterations) ---")

    # Define local runners
    def run_merge():
        return merge(base, override)

    def run_combine():
        return combine(base, override, op=Resolver.LAST)

    # --- Validation ---
    is_valid = True
    # The 'List-Heavy' and 'Stochastic' benchmarks have known, expected
    # differences in behavior. We handle them separately.
    if name == "List-Heavy Tree (Complex Lists)":
        merge_result = run_merge()
        combine_result = run_combine()
        merge_copy = merge_result.copy()
        combine_copy = combine_result.copy()
        del merge_copy["scalar_to_list"]
        del combine_copy["scalar_to_list"]
        is_valid = merge_copy == combine_copy
    elif name == "Stochastic Tree (Random Structure)":
        # For the stochastic test, correctness is not guaranteed due to random
        # type mismatches. We skip validation to focus on performance.
        print("NOTE: Skipping correctness validation for stochastic test.")
        pass
    else:
        is_valid = run_merge() == run_combine()

    if not is_valid:
        print(f"ERROR: {name} outputs do not match!")
        exit(1)

    # --- Timing ---
    merge_time = timeit.timeit(run_merge, number=iterations)
    combine_time = timeit.timeit(run_combine, number=iterations)

    print(f"merge()   : {merge_time:.4f} seconds")
    print(f"combine() : {combine_time:.4f} seconds")

    if merge_time < combine_time:
        factor = combine_time / merge_time
        print(f"Result    : `merge` is {factor:.2f}x faster.")
    else:
        factor = merge_time / combine_time
        print(f"Result    : `combine` is {factor:.2f}x faster.")


if __name__ == "__main__":
    # 1. Small Tree Benchmark (Balanced)
    run_benchmark(
        name="Small Tree (Balanced)",
        base=base_tree_small,
        override=override_tree_small,
        iterations=10_000
    )

    # 2. Wide Tree Benchmark (High Breadth)
    run_benchmark(
        name="Wide Tree (1,000+ Keys, High Breadth)",
        base=base_tree_wide,
        override=override_tree_wide,
        iterations=500
    )

    # 3. Deep Tree Benchmark (High Depth)
    run_benchmark(
        name="Deep Tree (100 Levels, High Depth)",
        base=base_tree_deep,
        override=override_tree_deep,
        iterations=1000
    )

    # 4. List-Heavy Benchmark (Complex Lists)
    run_benchmark(
        name="List-Heavy Tree (Complex Lists)",
        base=base_tree_list,
        override=override_tree_list,
        iterations=10_000
    )

    # 5. Large Enterprise Tree Benchmark
    run_benchmark(
        name="Large Enterprise Tree (2,500 Total Nodes)",
        base=base_tree_large,
        override=override_tree_large,
        iterations=50
    )

    # 6. Skewed Tree Benchmark
    run_benchmark(
        name="Skewed Tree (Deep and Wide)",
        base=base_tree_skewed,
        override=override_tree_skewed,
        iterations=500
    )
    
    # 7. Stochastic Tree Benchmark
    run_benchmark(
        name="Stochastic Tree (Random Structure)",
        base=base_tree_stochastic,
        override=override_tree_stochastic,
        iterations=1000
    )
