"""
Recipe 32: Combine with Decision Metrics

This recipe demonstrates how to combine two nested structures while simultaneously
generating companion "Decision Metric" trees.

These metrics allow tracking conflict resolution decisions (Provenance, Auditing,
and Changelogs) in a single high-performance recursive pass without altering
the schema or data types of the output tree.
"""
from mappingtools.operators import combine
from mappingtools.resolvers import DecisionMetric, NumericResolver, Resolver


def main():
    tree1 = {
        'a': 10,
        'b': {'c': 100},
        'd': [1, 2],
    }

    tree2 = {
        'a': 20,
        'b': {'c': 200, 'e': 300},
        'd': [3],
    }

    print("--- 1. Single Metric: Provenance (LAST wins) ---")
    combined, metrics = combine(
        tree1, tree2, Resolver.LAST, [DecisionMetric.PROVENANCE]
    )
    prov = metrics["PROVENANCE"]
    print("Combined:", combined)
    print("Provenance (0: tree1, 1: tree2):", prov)
    assert combined["a"] == 20
    assert prov["a"] == 1
    assert prov["b"]["e"] == 1
    assert prov["d"] == [1, 0]

    print("\n--- 2. Single Metric: Audit Mismatches ---")
    combined, metrics = combine(
        tree1, tree2, Resolver.LAST, [DecisionMetric.AUDIT]
    )
    audit = metrics["AUDIT"]
    print("Combined:", combined)
    print("Audit Log:", audit)
    assert audit["a"] == "conflict: 10 vs 20 -> 20"
    assert audit["b"]["e"] == "clean"

    print("\n--- 3. Multiple Metrics in a Single Pass ---")
    combined, metrics = combine(
        tree1,
        tree2,
        NumericResolver.SUM,
        [DecisionMetric.PROVENANCE, DecisionMetric.AUDIT, DecisionMetric.CHANGELOG]
    )
    print("Combined:", combined)
    print("Provenance:", metrics["PROVENANCE"])
    print("Audit:", metrics["AUDIT"])
    print("Changelog:", metrics["CHANGELOG"])

    # 'a' is a sum conflict (aggregative), so provenance is None
    assert combined["a"] == 30
    assert metrics["PROVENANCE"]["a"] is None
    assert metrics["AUDIT"]["a"] == "conflict: 10 vs 20 -> 30"
    assert metrics["CHANGELOG"]["a"] == "updated"

    # 'e' only exists in tree2 (added relative to tree1)
    assert combined["b"]["e"] == 300
    assert metrics["PROVENANCE"]["b"]["e"] == 1
    assert metrics["CHANGELOG"]["b"]["e"] == "added"

    print("\n--- 4. Multi-Tree Reduction (Source Index Tracking) ---")
    trees = [
        {"a": 10, "b": 100},  # Index 0
        {"a": 20},            # Index 1
        {"a": 30, "b": 200, "c": 300}  # Index 2
    ]

    def map_provenance(tree, step_idx):
        if isinstance(tree, dict):
            return {k: map_provenance(v, step_idx) for k, v in tree.items()}
        elif isinstance(tree, list):
            return [map_provenance(v, step_idx) for v in tree]
        else:
            return step_idx if tree == 1 else tree

    acc_tree = trees[0]
    acc_prov = {"a": 0, "b": 0}

    for i in range(1, len(trees)):
        combined, metrics = combine(
            acc_tree, trees[i], Resolver.LAST, [DecisionMetric.PROVENANCE]
        )
        mapped_prov = map_provenance(metrics["PROVENANCE"], i)
        # Combine provenance trees: if step_val is 0, keep accumulator index, otherwise take step index
        acc_prov = combine(
            acc_prov,
            mapped_prov,
            op=lambda acc_val, step_val: acc_val if step_val == 0 else step_val
        )
        acc_tree = combined

    print("Combined:", acc_tree)
    print("Provenance:", acc_prov)
    assert acc_tree == {"a": 30, "b": 200, "c": 300}
    assert acc_prov == {"a": 2, "b": 2, "c": 2}


def test_main():
    main()


if __name__ == "__main__":
    main()
