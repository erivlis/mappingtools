"""
Recipe 28: Combine with Conflict Resolution

The standard `merge` operator is a "last-wins" monoid, which is perfect for
layering configurations. However, sometimes you need more control when two
trees have conflicting values at the same leaf path.

This recipe introduces the `combine` operator, a generalization of `merge` that
accepts an `op` strategy. This strategy can be a pre-built resolver enum
(`Resolver`, `NumericResolver`, `LogicalResolver`) or any custom callable
that takes `(old_value, new_value)` and returns a resolved value.
"""
import operator

from mappingtools.operators import combine
from mappingtools.resolvers import LogicalResolver, NumericResolver, Resolver


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
    last_wins = combine(tree1, tree2, op=Resolver.LAST)
    print(last_wins)
    assert last_wins['a'] == 99
    assert last_wins['b']['c'] == 98

    print("\n--- 2. FIRST ---")
    first_wins = combine(tree1, tree2, op=Resolver.FIRST)
    print(first_wins)
    assert first_wins['a'] == 1
    assert first_wins['b']['c'] == 2

    print("\n--- 3. SUM (NumericResolver) ---")
    # Use a built-in numeric aggregation
    summed = combine(tree1, tree2, op=NumericResolver.SUM)
    print(summed)
    assert summed['a'] == 100
    assert summed['b']['c'] == 100

    print("\n--- 4. FAIL (Strict Disjointness) ---")
    # Fails because 'a' and 'b.c' overlap
    try:
        combine(tree1, tree2, op=Resolver.FAIL)
    except ValueError as e:
        print(f"Successfully caught expected error: {e}")

    # This will succeed because the trees are disjoint
    disjoint_tree = {'e': 5}
    success = combine(tree1, disjoint_tree, op=Resolver.FAIL)
    print("Successfully combined disjoint trees.")
    assert success['e'] == 5

    print("\n--- 5. ALL (Lossless Tuple Accumulation) ---")
    # Preserves history linearly into a tuple
    all_history = combine(tree1, tree2, op=Resolver.ALL)
    print(all_history)
    assert all_history['a'] == (1, 99)
    assert all_history['b']['c'] == (2, 98)

    print("\n--- 6. VOID (Annihilation) ---")
    # The conflicting leaves are completely pruned from the tree
    void_tree = combine(tree1, tree2, op=Resolver.VOID)
    print(void_tree)
    assert 'a' not in void_tree
    assert 'c' not in void_tree['b']
    assert void_tree['b']['d'] == 97

    print("\n--- 7. Logical AND (Bitmasks and Sets) ---")
    # The logical resolvers handle truthiness, sets, and bitwise integers automatically.
    perms1 = {'write_cache': 0b101, 'tags': {'A', 'B'}}
    perms2 = {'write_cache': 0b011, 'tags': {'B', 'C'}}

    intersected = combine(perms1, perms2, op=LogicalResolver.AND)
    print(intersected)
    assert intersected['write_cache'] == 0b001
    assert intersected['tags'] == {'B'}

    print("\n--- 8. Custom Callable (String Concatenation) ---")
    str_tree1 = {'msg': "hello"}
    str_tree2 = {'msg': " world"}
    concatenated = combine(str_tree1, str_tree2, op=operator.add)
    print(concatenated)
    assert concatenated['msg'] == "hello world"


def test_main():
    main()


if __name__ == "__main__":
    main()
