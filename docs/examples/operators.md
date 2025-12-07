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

## keep

Yields subsets of mappings by retaining only the specified keys.

<!-- name: test_keep -->

!!! Example

    ```python linenums="1"
    from mappingtools.operators import keep
    
    mappings = [
        {'a': 1, 'b': 2, 'c': 3},
        {'a': 4, 'b': 5, 'd': 6}
    ]
    keys_to_keep = ['a', 'b']
    output = list(keep(keys_to_keep, *mappings))
    print(output)
    # output: [{'a': 1, 'b': 2}, {'a': 4, 'b': 5}]
    ```

!!! Warning "Deprecated (since v0.8.0)"
    Use a generator expression with a dictionary comprehension instead.
    See docstring for an example.

## remove

Yields mappings with the specified keys removed.
It takes an iterable of keys and multiple mapping objects and returns a generator
of mappings with those keys excluded.

<!-- name: test_remove -->
!!! Example

    ```python linenums="1"
    from mappingtools.operators import remove
    
    mappings = [
        {'a': 1, 'b': 2, 'c': 3},
        {'a': 4, 'b': 5, 'd': 6}
    ]
    keys_to_remove = ['a', 'b']
    output = list(remove(keys_to_remove, *mappings))
    print(output)
    # output: [{'c': 3}, {'d': 6}]
    ```

!!! Warning "Deprecated (since v0.8.0)"
    Use a generator expression with a dictionary comprehension instead.
    See docstring for an example.

## stream

Takes a mapping and an optional item factory function, and generates items from the mapping.
If the item factory is provided, it applies the factory to each key-value pair before yielding.

!!! Example
    <!-- name: test_stream -->
    ```python linenums="1"
    from collections import namedtuple
    
    from mappingtools.operators import stream
    
    
    def custom_factory(key, value):
        return f"{key}: {value}"
    
    
    my_mapping = {'a': 1, 'b': 2, 'c': 3}
    
    for item in stream(my_mapping, custom_factory):
        print(item)
    
    # output:
    # a: 1
    # b: 2
    # c: 3
    
    
    MyTuple = namedtuple('MyTuple', ['key', 'value'])
    data = {'a': 1, 'b': 2}
    
    for item in stream(data, MyTuple):
        print(item)
    
    
    # output:
    # MyTuple(key='a', value=1)
    # MyTuple(key='b', value=2)
    
    
    def record(k, v):
        return {'key': k, 'value': v}
    
    
    for item in stream(data, record):
        print(item)
    
    # output:
    # {'key': 'a', 'value': 1}
    # {'key': 'b', 'value': 2}
    ```

!!! Warning "Deprecated (since v0.8.0)"
    Use `mapping.items()` or a generator comprehension instead.
    See docstring for an example.

## stream_dict_records

Generates dictionary records from a given mapping, where each record contains a key-value pair from the mapping with
customizable key and value names.

!!! Example

    <!-- name: test_stream_dict_records -->
    
    ```python linenums="1"
    from mappingtools.operators import stream_dict_records
    
    mapping = {'a': 1, 'b': 2}
    records = stream_dict_records(mapping, key_name='letter', value_name='number')
    for record in records:
        print(record)
    # output:
    # {'letter': 'a', 'number': 1}
    # {'letter': 'b', 'number': 2}
    ```

!!! Warning "Deprecated (since v0.8.0)"
    Use a generator expression with a dictionary literal instead.
    See docstring for an example.
