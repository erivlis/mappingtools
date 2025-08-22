# MappingTools

> Do stuff with Mappings and more

This library provides utility functions for manipulating and transforming data structures which have or include
Mapping-like characteristics. Including inverting dictionaries, converting class like objects to dictionaries,
creating nested defaultdicts, and unwrapping complex objects.

<table>
  <tr style="vertical-align: middle;">
    <td>Package</td>
    <td>
      <img alt="PyPI - Version" class="off-glb" loading="lazy" src="https://img.shields.io/pypi/v/mappingtools.svg?logo=pypi&logoColor=lightblue">
      <img alt="PyPI - Status" class="off-glb" loading="lazy" src="https://img.shields.io/pypi/status/mappingtools.svg?logo=pypi&logoColor=lightblue">
      <img alt="PyPI - Python Version" class="off-glb" loading="lazy" src="https://img.shields.io/pypi/pyversions/mappingtools.svg?logo=python&label=Python&logoColor=lightblue">
      <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dd/mappingtools.svg?logo=pypi&logoColor=lightblue">
      <img alt="Libraries.io SourceRank" src="https://img.shields.io/librariesio/sourcerank/pypi/mappingtools.svg?logo=Libraries.io&label=SourceRank">
    </td>
  </tr>
  <tr>
    <td>Code</td>
    <td>
      <img alt="GitHub" src="https://img.shields.io/github/license/erivlis/mappingtools">
      <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/erivlis/mappingtools.svg?label=Size&logo=git">
      <img alt="GitHub last commit (by committer)" src="https://img.shields.io/github/last-commit/erivlis/mappingtools.svg?&logo=git">
      <a href="https://github.com/erivlis/mappingtools/graphs/contributors"><img alt="Contributors" src="https://img.shields.io/github/contributors/erivlis/mappingtools.svg?&logo=git"></a>
    </td>
  </tr>
  <tr>
    <td>Tools</td>
    <td>
      <a href="https://www.jetbrains.com/pycharm/"><img alt="PyCharm" src="https://img.shields.io/badge/PyCharm-FCF84A.svg?logo=PyCharm&logoColor=black&labelColor=21D789&color=FCF84A"></a>
      <a href="https://github.com/astral-sh/uv"><img alt="uv" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" style="max-width:100%;"></a>
      <a href="https://github.com/astral-sh/ruff"><img  alt="Ruff" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" style="max-width:100%;"></a>
      <!--a href="https://squidfunk.github.io/mkdocs-material/"><img src="https://img.shields.io/badge/Material_for_MkDocs-526CFE?&logo=MaterialForMkDocs&logoColor=white&labelColor=grey"></a-->
      <a href="https://hatch.pypa.io"><img alt="Hatch project" class="off-glb" loading="lazy" src="https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg"></a>
    </td>
  </tr>
  <tr>
    <td>CI/CD</td>
    <td>
      <a href="https://github.com/erivlis/mappingtools/actions/workflows/test.yml"><img alt="Test" src="https://github.com/erivlis/mappingtools/actions/workflows/test.yml/badge.svg"></a>
      <a href="https://github.com/erivlis/mappingtools/actions/workflows/publish.yml"><img alt="Publish" src="https://github.com/erivlis/mappingtools/actions/workflows/test-beta.yml/badge.svg"></a>
      <a href="https://github.com/erivlis/mappingtools/actions/workflows/publish.yml"><img alt="Publish" src="https://github.com/erivlis/mappingtools/actions/workflows/publish.yml/badge.svg"></a>
      <!--a href="https://github.com/erivlis/mappingtools/actions/workflows/publish-docs.yaml"><img alt="Publish Docs" src="https://github.com/erivlis/mappingtools/actions/workflows/publish-docs.yaml/badge.svg"></a-->
    </td>
  </tr>
  <tr>
    <td>Scans</td>
    <td>
      <a href="https://codecov.io/gh/erivlis/mappingtools"><img alt="Coverage" src="https://codecov.io/gh/erivlis/mappingtools/graph/badge.svg?token=POODT8M9NV"/></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Quality Gate Status" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=alert_status"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Security Rating" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=security_rating"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Maintainability Rating" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=sqale_rating"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Reliability Rating" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=reliability_rating"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Lines of Code" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=ncloc"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Vulnerabilities" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=vulnerabilities"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Bugs" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=bugs"></a>
      <a href="https://app.codacy.com/gh/erivlis/mappingtools/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade"><img alt="Codacy Quality" src="https://app.codacy.com/project/badge/Grade/8b83a99f939b4883ae2f37d7ec3419d1"></a>
      <a href="https://app.codacy.com/gh/erivlis/mappingtools/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage"><img alt="Codacy Coverage" src="https://app.codacy.com/project/badge/Coverage/8b83a99f939b4883ae2f37d7ec3419d1"/></a>
      <a href="https://www.codefactor.io/repository/github/erivlis/mappingtools/overview/main"><img src="https://www.codefactor.io/repository/github/erivlis/mappingtools/badge/main" alt="CodeFactor" /></a>
      <a href="https://snyk.io/test/github/erivlis/mappingtools"><img alt="Snyk" src="https://snyk.io/test/github/erivlis/mappingtools/badge.svg"></a>
    </td>
  </tr>
</table>

## Overview

The **_MappingTools_** library is organized into several namespaces, each containing specific functionalities for
manipulating and transforming data structures. Below is a brief description of the main namespaces within the library:

- **collectors** - This namespace contains classes and functions for collecting and categorizing data items into mappings.
  - **CategoryCounter** - Extends a dictionary to count occurrences of data items categorized by multiple categories.
  - **MappingCollector** - Collects key-value pairs into an internal mapping based on different modes (ALL, COUNT,
  DISTINCT, FIRST, LAST).
  - **nested_defaultdict** - Creates a nested `defaultdict` with specified depth and factory.
- **operators** - This namespace provides functions that perform operations on mappings.
  - **distinct** - Yields distinct values for a specified key across multiple mappings.
  - **flattened** - Converts a nested mapping structure into a single-level dictionary by flattening the keys into tuples.
  - **inverse** - generates an inverse Mapping by swapping keys and values.
  - **keep** - Yields subsets of mappings by retaining the specified keys.
  - **remove** - Yields subsets mappings with the specified keys removed.
  - **stream** - Generates items from a mapping, optionally applying a factory function to each key-value pair.
  - **stream_dict_records** - Generates dictionary records from a mapping with customizable key and value names.
  - **unique_string** -
- **transformers** - This namespace includes functions that reshape objects while maintaining the consistency of their structure.
  - **listify** - Transforms complex objects into a list of dictionaries with key and value pairs.
  - **minify** - The minify function is used to shorten the keys of an object using a specified alphabet.
  - **simplify** - Converts objects to strictly structured dictionaries.
  - **strictify** - Applies a strict structural conversion to an object using optional converters for keys and values.
  - **stringify** - Converts an object into a string representation by recursively processing it based on its type.

## Examples

### Collectors

Collectors are classes that collect data items into a Mapping.

#### CategoryCounter

The CategoryCounter class extends a dictionary to count occurrences of data items categorized by multiple categories.
It maintains a total count of all data items and allows categorization using direct values or functions.

<!-- name: test_category_counter -->

```python
from mappingtools.collectors import CategoryCounter

counter = CategoryCounter()

for fruit in ['apple', 'banana', 'apple']:
    counter.update({fruit: 1}, type='fruit', char_count=len(fruit), unique_char_count=len(set(fruit)))

print(counter.total)
# Output: Counter({'apple': 2, 'banana': 1})

print(counter)
# output: CategoryCounter({'type': defaultdict(<class 'collections.Counter'>, {'fruit': Counter({'apple': 2, 'banana': 1})}), 'char_count': defaultdict(<class 'collections.Counter'>, {5: Counter({'apple': 2}), 6: Counter({'banana': 1})}), 'unique_char_count': defaultdict(<class 'collections.Counter'>, {4: Counter({'apple': 2}), 3: Counter({'banana': 1})})})
```

#### MappingCollector

A class designed to collect key-value pairs into an internal mapping based on different modes.
It supports modes like ALL, COUNT, DISTINCT, FIRST, and LAST, each dictating how key-value pairs are
collected.

<!-- name: test_mapping_collector -->

```python
from mappingtools.collectors import MappingCollector, MappingCollectorMode

collector = MappingCollector(MappingCollectorMode.ALL)
collector.add('a', 1)
collector.add('a', 2)
collector.collect([('b', 3), ('b', 4)])
print(collector.mapping)
# output: {'a': [1, 2], 'b': [3, 4]}
```

####  nested_defaultdict

Creates a nested defaultdict with specified depth and factory.

<!-- name: test_nested_defaultdict -->

```python
from mappingtools.collectors import nested_defaultdict

nested_dd = nested_defaultdict(1, list)
nested_dd[0][1].append('value')
print(nested_dd)
# output: defaultdict(<function nested_defaultdict.<locals>.factory at ...>, {0: defaultdict(<function nested_defaultdict.<locals>.factory at ...>, {1: ['value']})})
```

### `Operators`
### Operators

Operators are functions that perform operations on Mappings.

#### distinct

Yields distinct values for a specified key across multiple mappings.

<!-- name: test_distinct -->

```python
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

#### flattened

The flattened function takes a nested mapping structure and converts it into a single-level dictionary by flattening the
keys into tuples.

<!-- name: test_flattened -->

```python
from mappingtools.operators import flattened

nested_dict = {
    'a': {'b': 1, 'c': {'d': 2}},
    'e': 3
}
flat_dict = flattened(nested_dict)
print(flat_dict)
# output: {('a', 'b'): 1, ('a', 'c', 'd'): 2, ('e',): 3}
```

#### inverse

Swaps keys and values in a dictionary.

<!-- name: test_inverse -->

```python
from mappingtools.operators import inverse

original_mapping = {'a': {1, 2}, 'b': {3}}
inverted_mapping = inverse(original_mapping)
print(inverted_mapping)
# output: defaultdict(<class 'set'>, {1: {'a'}, 2: {'a'}, 3: {'b'}})
```

#### keep

Yields subsets of mappings by retaining only the specified keys.

<!-- name: test_keep -->

```python
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

#### remove

Yields mappings with specified keys removed. It takes an iterable of keys and multiple mappings, and returns a generator
of mappings with those keys excluded.

<!-- name: test_remove -->

```python
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

#### stream

Takes a mapping and an optional item factory function, and generates items from the mapping.
If the item factory is provided, it applies the factory to each key-value pair before yielding.

<!-- name: test_stream -->

```python
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

#### stream_dict_records

generates dictionary records from a given mapping, where each record contains a key-value pair from the mapping with
customizable key and value names.

<!-- name: test_stream_dict_records -->

```python
from mappingtools.operators import stream_dict_records

mapping = {'a': 1, 'b': 2}
records = stream_dict_records(mapping, key_name='letter', value_name='number')
for record in records:
    print(record)
# output:
# {'letter': 'a', 'number': 1}
# {'letter': 'b', 'number': 2}
```

#### unique_string

The unique_strings function generates an endless stream of the shortest possible strings using a specified alphabet.
By default, it uses the uppercase English alphabet (string.ascii_uppercase).
The function can generate strings of a fixed length or start with the shortest strings and increase the length
indefinitely.

<!-- name: test_unique_string -->

```python
from mappingtools.operators import unique_strings

alphabet1 = 'AB'
string_length = 3
generator1 = unique_strings(alphabet1, string_length)

print('strings of length 3 created from alphabet: ', alphabet1)
for s in list(generator1):
    print(s)

alphabet2 = '01'
generator2 = unique_strings(alphabet2)

print('First 10 strings of all lengths created from alphabet: ', alphabet2)
for _ in range(10):
    print(next(generator2))
```

### Transformers

Transformers are functions that reshape an object, while maintaining the consistency of the structure.

#### listify

Transforms complex objects into a list of dictionaries with key and value pairs.

<!-- name: test_listify -->

```python
from mappingtools.transformers import listify

wrapped_data = {'key1': {'subkey': 'value'}, 'key2': ['item1', 'item2']}
unwrapped_data = listify(wrapped_data)
print(unwrapped_data)
# output: [{'key': 'key1', 'value': [{'key': 'subkey', 'value': 'value'}]}, {'key': 'key2', 'value': ['item1', 'item2']}]
```

#### minify

The minify function is used to shorten the keys of an object using a specified alphabet.
This function can be particularly useful for reducing the size of data structures, making
them more efficient for storage or transmission.

<!-- name: test_minify -->

```python
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

#### simplify

Converts objects to strictly structured dictionaries.

<!-- name: test_simplify -->

```python
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

#### strictify

Applies a strict structural conversion to an object using optional converters for keys and values.

<!-- name: test_strictify -->

##### Example 1

```python
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

#### `stringify`
#### stringify

Converts an object into a string representation by recursively processing it based on its type.

<!-- Name: test_stringify -->

```python
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

## Development

### Ruff

```shell
ruff check src

ruff check tests
```

### Test

#### Standard (cobertura) XML Coverage Report

```shell
python -m pytest tests -n auto --cov=src --cov-branch --doctest-modules --cov-report=xml
```

#### HTML Coverage Report

```shell
python -m pytest tests -n auto --cov=src --cov-branch --doctest-modules --cov-report=html
```
