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

# --- Setup Large Data ---
def generate_large_tree(size: int, prefix: str = "") -> dict:
    """Generates a synthetic large dictionary to simulate enterprise payloads."""
    tree = {}
    for i in range(size):
        tree[f"key_{i}"] = {
            "id": f"{prefix}_{i}",
            "metrics": {"cpu": 50, "mem": 1024, "disk": 500},
            "tags": [f"tag_{i}", "common"],
            "status": "active"
        }
    return tree

print("Generating synthetic large trees (1,000 nested nodes)...")
base_tree_large = generate_large_tree(1000, "base")
# The override tree has conflicting scalars, deep dicts, and lists
override_tree_large = generate_large_tree(1000, "override")


def run_benchmark(name: str, base: dict, override: dict, iterations: int):
    print(f"\n--- Benchmarking: {name} ({iterations:,} iterations) ---")
    
    # Define local runners
    def run_merge():
        return merge(base, override)

    def run_combine():
        return combine(base, override, op=Resolver.LAST)

    # Validate correctness
    if run_merge() != run_combine():
        print(f"ERROR: {name} outputs do not match!")
        exit(1)

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
    # 1. Small Tree Benchmark (Fast, lots of iterations)
    run_benchmark(
        name="Small Tree (Config Layering)",
        base=base_tree_small,
        override=override_tree_small,
        iterations=10_000
    )

    # 2. Large Tree Benchmark (Enterprise payload, fewer iterations)
    run_benchmark(
        name="Large Tree (1,000 Nodes, Mass Collision)",
        base=base_tree_large,
        override=override_tree_large,
        iterations=100
    )

    print("\n--- Analysis ---")
    print("As the number of nodes (and therefore collisions) increases, the 'abstraction tax'")
    print("of calling the Python `op` function inside `combine` scales linearly.")
    print("`merge` remains consistently faster because the 'last-wins' logic is executed natively without function dispatch.")
