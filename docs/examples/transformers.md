---
icon: lucide/square-function
---

# Transformers

!!! Abstract
    Transformers are functions that reshape an object, while maintaining the consistency of the structure.

## listify

Transforms complex objects into a list of dictionaries with key and value pairs.

<!-- name: test_listify -->

```python linenums="1"
from mappingtools.transformers import listify

wrapped_data = {'key1': {'subkey': 'value'}, 'key2': ['item1', 'item2']}
unwrapped_data = listify(wrapped_data)
print(unwrapped_data)
# output: [{'key': 'key1', 'value': [{'key': 'subkey', 'value': 'value'}]}, {'key': 'key2', 'value': ['item1', 'item2']}]
```

## minify

The minify function is used to shorten the keys of an object using a specified alphabet.
This function can be particularly useful for reducing the size of data structures, making
them more efficient for storage or transmission.

<!-- name: test_minify -->

```python linenums="1"
from mappingtools.transformers import minify

data = [
    {
        'first_name': 'John',
        'last_name': 'Doe',
        'age': 30,
        'address': {
            'street': '123 Main St',
            'city': 'New York',
            'state': 'CA'
        }
    },
    {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'age': 25,
        'address': {
            'street': '456 Rodeo Dr',
            'city': 'Los Angeles',
            'state': 'CA'
        }
    }
]

# Minify the dictionary keys
minified_dict = minify(data)

print(minified_dict)
# [{'A': 'John', 'B': 'Doe', 'C': 30, 'D': {'E': '123 Main St', 'F': 'New York', 'G': 'CA'}}, {'A': 'Jane', 'B': 'Smith', 'C': 25, 'D': {'E': '456 Rodeo Dr', 'F': 'Los Angeles', 'G': 'CA'}}]
```

## simplify

Converts objects to strictly structured dictionaries.

<!-- name: test_simplify -->

```python linenums="1"
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

from mappingtools.transformers import simplify

data = {'key1': 'value1', 'key2': ['item1', 'item2']}
simplified_data = simplify(data)
print(simplified_data)
# Output: {'key1': 'value1', 'key2': ['item1', 'item2']}

counter = Counter({'a': 1, 'b': 2})
print(counter)
# Output: Counter({'b': 2, 'a': 1})

simplified_counter = simplify(counter)
print(simplified_counter)


# output: {'a': 1, 'b': 2}


@dataclass
class SampleDataClass:
    a: int
    b: int
    aa: str
    bb: str
    c: list[int]
    d: Mapping
    e: datetime


sample_datetime = datetime(2024, 7, 22, 21, 42, 17, 314159)
sample_dataclass = SampleDataClass(1, 2, '11', '22', [1, 2], {'aaa': 111, 'bbb': '222'}, sample_datetime)
print(sample_dataclass)
# output: SampleDataClass(a=1, b=2, aa='11', bb='22', c=[1, 2], d={'aaa': 111, 'bbb': '222'}, e=datetime.datetime(2024, 7, 22, 21, 42, 17, 314159))

simplified_sample_dataclass = simplify(sample_dataclass)
print(simplified_sample_dataclass)
# output: {'a': 1, 'aa': '11', 'b': 2, 'bb': '22', 'c': [1, 2], 'd': {'aaa': 111, 'bbb': '222'}, 'e': datetime.datetime(2024, 7, 22, 21, 42, 17, 314159)}
```

## strictify

Applies a strict structural conversion to an object using optional converters for keys and values.

<!-- name: test_strictify -->

##### Example 1

```python linenums="1"
from mappingtools.transformers import strictify


def uppercase_key(key):
    return key.upper()


def double_value(value):
    return value * 2


data = {'a': 1, 'b': 2}
result = strictify(data, key_converter=uppercase_key, value_converter=double_value)
print(result)
# output: {'A': 2, 'B': 4}
```

##### Example 2

```python linenums="1"
from mappingtools.transformers import strictify

data = [
    {
        'first_name': 'John',
        'last_name': 'Doe',
        'age': 30,
        'address': {
            'street': '123 Main St',
            'city': 'New York',
            'state': 'CA'
        }
    },
    {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'age': 25,
        'address': {
            'street': '456 Rodeo Dr',
            'city': 'Los Angeles',
            'state': 'CA'
        }
    }
]


def key_converter(key):
    return key.replace('_', ' ').title().replace(' ', '')


result = strictify(data, key_converter=key_converter)
print(result)
# output: 
# [
#     {
#         'FirstName': 'John',
#         'LastName': 'Doe',
#         'Age': 30,
#         'Address': {
#             'Street': '123 Main St',
#             'City': 'New York',
#             'State': 'CA'
#         }
#     },
#     {
#         'FirstName': 'Jane',
#         'LastName': 'Smith',
#         'Age': 25,
#         'Address': {
#             'Street': '456 Rodeo Dr',
#             'City': 'Los Angeles',
#             'State': 'CA'
#         }
#     }
# ]
```

## stringify

Converts an object into a string representation by recursively processing it based on its type.

<!-- Name: test_stringify -->

```python linenums="1"
from mappingtools.transformers import stringify

data = {'key1': 'value1', 'key2': 'value2'}
result = stringify(data)

print(result)
# output: "key1=value1, key2=value2"

data = [1, 2, 3]
result = stringify(data)

print(result)
# output: "[1, 2, 3]"
```
