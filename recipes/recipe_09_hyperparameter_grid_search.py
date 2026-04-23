"""
Recipe 09: Cartesian Grid Search (itertools.product + merge)

When performing hyperparameter tuning or parameterized testing, you often
need to generate a vast matrix of configuration objects from a base template.

By combining `itertools.product` to generate combinations of values,
and our `merge` Monoid to immutably stamp those overrides onto a base tree,
we can instantly yield thousands of distinct, fully-formed configurations.
"""

import itertools
import json
from functools import reduce
from operator import mul

from mappingtools.operators import merge


def main():
    # 1. Our base, default configuration template
    base_config = {
        "architecture": "transformer",
        "dataset": "corpus_v2",
        "training": {
            "epochs": 100,
            "optimizer": "adam",
            "batch_size": 32,
            "learning_rate": 0.01,
            "dropout": 0.1,
        },
    }

    # 2. The hyperparameter space we want to explore
    search_space = {
        "batch_size": [16, 64, 128],
        "learning_rate": [0.05, 0.001],
        "dropout": [0.1, 0.5],
    }

    # 3. Extract the keys and value lists to feed into itertools.product
    keys = list(search_space.keys())
    value_lists = list(search_space.values())

    print("--- Generating Configuration Matrix ---")
    print("Base Configuration Template defined.")

    lengths = [len(v) for v in value_lists]
    total_combinations = reduce(mul, lengths) if lengths else 0
    search_space_str = " x ".join(map(str, lengths))
    print(f"Search Space: {search_space_str} = {total_combinations} combinations.\n")

    # 4. Generate the Cartesian product of all possible parameter combinations
    for values_tuple in itertools.product(*value_lists):

        # 5. Build an "override" dictionary for this specific combination.
        override_tree = {"training": {keys[i]: values_tuple[i] for i in range(len(keys))}}

        # 6. Use our pure Monoid `merge` to stamp the override onto the base config.
        test_config = merge(base_config, override_tree)

        # In a real scenario, you would yield this `test_config` to your test runner
        # or ML training loop. Here, we just print a summary.
        t_conf = test_config["training"]
        print(
            f"Yielding Config -> Batch: {t_conf['batch_size']:<3} | "
            f"LR: {t_conf['learning_rate']:<5} | "
            f"Dropout: {t_conf['dropout']}"
        )

    # Prove immutability
    print("\n--- Verification ---")
    print("Base config remains unmodified:")
    print(json.dumps(base_config["training"], indent=2))


def test_main():
    main()


if __name__ == "__main__":
    main()
