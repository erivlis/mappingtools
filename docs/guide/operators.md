---
icon: lucide/square-asterisk
---

# Operators

!!! Abstract
Operators are functions that perform operations on Mappings.

## distinct

Yields distinct values for a specified key across multiple mappings.

!!! Example

    <!-- name: test_distinct -->
    
    ```python linenums="1"
    from mappingtools.operators import distinct
    
    mappings = [
        {'a': 1, 'b': 2},
        {'a': 2, 'b': 3},
        {'a': 1, 'b': 4}
    ]
    distinct_values = list(distinct('a', *mappings))
    print(distinct_values)
    # output: [1, 2]
    ```

## flatten

The flatten function takes a nested mapping structure and converts it into a single-level dictionary by flattening the
keys into tuples.

!!! Example

    <!-- name: test_flattened -->
    
    ```python linenums="1"
    from mappingtools.operators import flatten
    
    nested_dict = {
        'a': {'b': 1, 'c': {'d': 2}},
        'e': 3
    }
    flat_dict = flatten(nested_dict)
    print(flat_dict)
    # output: {('a', 'b'): 1, ('a', 'c', 'd'): 2, ('e',): 3}
    ```

## inverse

Swaps keys and values in a dictionary.

!!! Example

    <!-- name: test_inverse -->
    
    ```python linenums="1"
    from mappingtools.operators import inverse
    
    original_mapping = {'a': {1, 2}, 'b': {3}}
    inverted_mapping = inverse(original_mapping)
    print(inverted_mapping)
    # output: defaultdict(<class 'set'>, {1: {'a'}, 2: {'a'}, 3: {'b'}})
    ```

## merge

A pure function (Monoid operation) to deeply merge two recursive tree structures.
The merging strategy resolves conflicts by overwriting existing values with new ones (right-side precedence).

Mathematically, this operation forms a composite Monoid:

- Last Monoid (Scalar Fallback): When resolving conflicts between simple values, the right-hand
  side (`tree2`) wins.
- Pointwise Monoid (Dictionary Merge): If the values are dictionaries, they are merged by key,
  recursively calling `merge` on the values.
- Zip Monoid (List Merge): If both are lists, they are zipped and merged positionally,
  substituting `MISSING` for missing indices.
- Free Monoid (Mixed List/Scalar): If one is a list and the other is a scalar/dict,
  it concatenates (appends/prepends).

Because it forms a Monoid, this function can be used with `functools.reduce` to collect an iterable of trees into a
single structure.

!!! Example "Merging two trees directly"

    <!-- name: test_merge -->

    ```python linenums="1"
    from mappingtools.operators import merge
    
    tree1 = {"a": 1, "b": [1, 2]}
    tree2 = {"b": [3], "c": 4}
    
    merged = merge(tree1, tree2)
    print(merged)
    # output: {'a': 1, 'b': [3, 2], 'c': 4}
    ```

!!! Example "Reducing an iterable of trees"

    Using Python's standard `functools.reduce`, we can easily merge an entire sequence of nested structures.

    <!-- name: test_merge_reduce -->

    ```python linenums="1"
    from functools import reduce
    from mappingtools.operators import merge

    trees = [
        {"a": 1, "b": {"c": 2}},
        {"b": {"d": 3}},
        {"a": 10}, # Overwrites previous "a"
    ]

    merged = reduce(merge, trees)
    print(merged)
    # output: {'a': 10, 'b': {'c': 2, 'd': 3}}
    ```

!!! Example "Deep merging with Lenses"

    If you need to merge data into a specific, deeply nested location of a larger tree, you can compose the `merge`
    function with an Optic (`Lens`).
    This avoids modifying the pure `merge` function with path traversal logic.

    <!-- name: test_merge_lens -->

    ```python linenums="1"
    from mappingtools.operators import merge
    from mappingtools.optics import Lens

    system_state = {"system": {"config": {"retries": 3}}}
    new_config = {"timeout": 30}

    # Focus specifically on the 'config' node inside 'system'
    config_lens = Lens.path("system", "config")

    # Apply the merge function OVER the focused node
    new_state = config_lens.modify(
        system_state, 
        lambda old: merge(old, new_config)
    )

    print(new_state)
    # output: {'system': {'config': {'retries': 3, 'timeout': 30}}}
    ```

## pivot

Reshapes a list of mappings into a nested dictionary based on index and column keys.
Supports different aggregation modes via `Aggregation`.

!!! Example

    <!-- name: test_pivot -->
    
    ```python linenums="1"
    from mappingtools.operators import pivot
    from mappingtools.aggregation import Aggregation
    
    data = [
        {"city": "NYC", "month": "Jan", "temp": 10},
        {"city": "NYC", "month": "Feb", "temp": 12},
        {"city": "LON", "month": "Jan", "temp": 5},
        {"city": "NYC", "month": "Jan", "temp": 20}, # Duplicate
    ]
    
    # Default mode (LAST wins)
    result = pivot(data, index="city", columns="month", values="temp")
    print(result)
    # output: {'NYC': {'Jan': 20, 'Feb': 12}, 'LON': {'Jan': 5}}
    
    # Aggregation mode: ALL (collect list)
    result_all = pivot(data, index="city", columns="month", values="temp", aggregation=Aggregation.ALL)
    print(result_all["NYC"]["Jan"])
    # output: [10, 20]
    ```

## reshape

A generalization of `pivot` that creates nested dictionaries (tensors) of arbitrary depth.
While `pivot` is limited to 2 dimensions (Index, Columns), `reshape` accepts a sequence of keys to define the hierarchy.

!!! Example

    <!-- name: test_reshape -->

    ```python linenums="1"
    from mappingtools.operators import reshape
    from mappingtools.aggregation import Aggregation

    data = [
        {"country": "US", "state": "NY", "city": "NYC", "pop": 8.4},
        {"country": "US", "state": "CA", "city": "LA", "pop": 3.9},
        {"country": "UK", "state": "ENG", "city": "LON", "pop": 8.9},
        {"country": "US", "state": "NY", "city": "Albany", "pop": 0.1},
    ]

    # 3-Level Hierarchy: Country -> State -> City
    tree = reshape(data, keys=["country", "state", "city"], value="pop")
    
    print(tree["US"]["NY"]["NYC"])
    # output: 8.4

    # Aggregation: Sum population by Country -> State
    # (City is marginalized/ignored)
    state_pop = reshape(
        data, 
        keys=["country", "state"], 
        value="pop", 
        aggregation=Aggregation.SUM
    )
    
    print(state_pop["US"]["NY"])
    # output: 8.5

    # Deep Keys (using Lenses or Callables)
    # If your data is nested, you can use callables to extract keys.
    # This works perfectly with the library's `Lens` or standard `operator.itemgetter`.
    
    nested_data = [
        {"id": 1, "meta": {"region": "US"}, "val": 10},
        {"id": 2, "meta": {"region": "UK"}, "val": 20},
    ]
    
    # Group by meta.region
    deep_tree = reshape(
        nested_data, 
        keys=[lambda x: x["meta"]["region"]], 
        value="val"
    )
    # output: {'US': 10, 'UK': 20}
    ```

## rekey

Transforms keys of a mapping based on a factory function of `(key, value)`.
This allows "re-indexing" a mapping where the new key depends on the content
of the value or a combination of the old key and value. Collisions are
handled according to the specified aggregation.

!!! Example

    <!-- name: test_rekey -->
    
    ```python linenums="1"
    from mappingtools.operators import rekey
    from mappingtools.aggregation import Aggregation
    
    mapping = {
        "alice": {"dept": "IT", "id": 1},
        "bob": {"dept": "HR", "id": 2},
        "charlie": {"dept": "IT", "id": 3},
    }
    
    # Re-index by 'id'
    by_id = rekey(mapping, lambda k, v: v["id"])
    print(by_id[1])
    # output: {'dept': 'IT', 'id': 1}
    
    # Group by 'dept' using Aggregation.ALL
    by_dept = rekey(mapping, lambda k, v: v["dept"], aggregation=Aggregation.ALL)
    print(list(by_dept.keys()))
    # output: ['IT', 'HR']
    print(len(by_dept["IT"]))
    # output: 2
    ```

## rename

Renames keys in a mapping based on a mapper (Mapping or Callable).
If a key is not present in the mapper, it remains unchanged. Collisions
are handled according to the specified aggregation.

!!! Example

    <!-- name: test_rename -->
    
    ```python linenums="1"
    from mappingtools.operators import rename
    
    data = {"usr_id": 1, "usr_name": "Alice", "email": "alice@example.com"}
    
    # Using a mapping
    renamed = rename(data, {"usr_id": "id", "usr_name": "name"})
    print(list(renamed.keys()))
    # output: ['id', 'name', 'email']
    
    # Using a callable
    renamed_upper = rename(data, str.upper)
    print(list(renamed_upper.keys()))
    # output: ['USR_ID', 'USR_NAME', 'EMAIL']
    ```
