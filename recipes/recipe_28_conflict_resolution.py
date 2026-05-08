"""
Recipe 28: Lift with Conflict Resolution

The standard `merge` operator is a "last-wins" monoid, which is perfect for
layering configurations. However, sometimes you need more control when two
trees have conflicting values at the same leaf path.

This recipe introduces the `lift` operator, a generalization of `merge` that
accepts an `op` strategy. This strategy can be a pre-built `Resolver`
enum or any custom callable that takes `(old_value, new_value)` and returns a
resolved value.
"""

from mappingtools.operators import lift
from mappingtools.resolvers import Resolver


def main():
    tree1 = {
        'a': 1,
        'b': {'c': 2},
        'd': [10, 20],
    }

    tree2 = {
        'a': 99,
        'b': {'c': 98, 'd': 97},
        'd': [30],
    }

    print("--- 1. Default (LAST) ---")
    # Equivalent to the standard `merge`
    last_wins = lift(tree1, tree2, op=Resolver.LAST)
    print(last_wins)
    assert last_wins['a'] == 99
    assert last_wins['b']['c'] == 98

    print("\n--- 2. FIRST ---")
    first_wins = lift(tree1, tree2, op=Resolver.FIRST)
    print(first_wins)
    assert first_wins['a'] == 1
    assert first_wins['b']['c'] == 2

    print("\n--- 3. SUM ---")
    # Use a built-in numeric aggregation
    summed = lift(tree1, tree2, op=Resolver.SUM)
    print(summed)
    assert summed['a'] == 100
    assert summed['b']['c'] == 100

    print("\n--- 4. FAIL (Strict Disjointness) ---")
    # Fails because 'a' and 'b.c' overlap
    try:
        lift(tree1, tree2, op=Resolver.FAIL)
    except ValueError as e:
        print(f"Successfully caught expected error: {e}")

    # This will succeed because the trees are disjoint
    disjoint_tree = {'e': 5}
    success = lift(tree1, disjoint_tree, op=Resolver.FAIL)
    print("Successfully combined disjoint trees.")
    assert success['e'] == 5

    print("\n--- 5. Custom Callable (String Concatenation) ---")
    str_tree1 = {'msg': "hello"}
    str_tree2 = {'msg': " world"}
    concatenated = lift(str_tree1, str_tree2, op=lambda old, new: old + new)
    print(concatenated)
    assert concatenated['msg'] == "hello world"


def test_main():
    main()


if __name__ == "__main__":
    main()
