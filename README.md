# mappingtools

This library provides utility functions for manipulating and transforming data structures,
including inverting dictionaries, converting objects to dictionaries, creating nested defaultdicts,
and unwrapping complex objects.

## Usage

### `dictify`

Converts objects to dictionaries using handlers for mappings, iterables, and classes.

```python
from mappingtools import dictify

data = {'key1': 'value1', 'key2': ['item1', 'item2']}
dictified_data = dictify(data)
print(dictified_data)
# Output: {'key1': 'value1', 'key2': ['item1', 'item2']}
```

### `distinct`

Yields distinct values for a specified key across multiple mappings.

```python
from mappingtools import distinct

mappings = [
    {'a': 1, 'b': 2},
    {'a': 2, 'b': 3},
    {'a': 1, 'b': 4}
]
distinct_values = list(distinct('a', *mappings))
print(distinct_values)
# Output: [1, 2]
```

### `keep`

Yields subsets of mappings by retaining only the specified keys.

```python
from mappingtools import keep

mappings = [
    {'a': 1, 'b': 2, 'c': 3},
    {'a': 4, 'b': 5, 'd': 6}
]
keys_to_keep = ['a', 'b']
result = list(keep(keys_to_keep, *mappings))
# result: [{'a': 1, 'b': 2}, {'a': 4, 'b': 5}]
```

### `inverse`

Swaps keys and values in a dictionary.

```python
from mappingtools import inverse

original_mapping = {'a': {1, 2}, 'b': {3}}
inverted_mapping = inverse(original_mapping)
print(inverted_mapping)
# Output: {1: 'a', 2: 'a', 3: 'b'}
```

### `nested_defaultdict`

Creates a nested defaultdict with specified depth and factory.

```python
from mappingtools import nested_defaultdict

nested_dd = nested_defaultdict(2, list)
nested_dd[0][1].append('value')
print(nested_dd)
# Output: defaultdict(<function nested_defaultdict.<locals>.factory at ...>, {0: defaultdict(<function nested_defaultdict.<locals>.factory at ...>, {1: ['value']})})
```

### `remove`

Yields mappings with specified keys removed. It takes an iterable of keys and multiple mappings, and returns a generator
of mappings with those keys excluded.

```python
from mappingtools import remove

mappings = [
    {'a': 1, 'b': 2, 'c': 3},
    {'a': 4, 'b': 5, 'd': 6}
]
keys_to_remove = ['a', 'b']
result = list(remove(keys_to_remove, *mappings))
# result: [{'c': 3}, {'d': 6}]

```

### `unwrap`

Transforms complex objects into a list of dictionaries with key and value pairs.

```python
from mappingtools import unwrap

wrapped_data = {'key1': {'subkey': 'value'}, 'key2': ['item1', 'item2']}
unwrapped_data = unwrap(wrapped_data)
print(unwrapped_data)
# Output: [{'key': 'key1', 'value': [{'key': 'subkey', 'value': 'value'}]}, {'key': 'key2', 'value': ['item1', 'item2']}]
```

## Development

### Ruff

```shell
ruff check src
```

### Test

#### Standard (cobertura) XML Coverage Report

```shell
 python -m pytest tests -n auto --cov=src --cov-branch --doctest-modules --cov-report=xml --junitxml=test_results.xml
```

#### HTML Coverage Report

```shell
python -m pytest tests -n auto --cov=src --cov-branch --doctest-modules --cov-report=html --junitxml=test_results.xml
```