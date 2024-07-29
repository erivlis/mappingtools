# MappingTools

This library provides utility functions for manipulating and transforming data structures which have or include
Mapping-like characteristics. Including inverting dictionaries, converting class like objects to dictionaries, creating
nested defaultdicts, and unwrapping complex objects.

<table>
  <tr style="vertical-align: middle;">
    <td>Package</td>
    <td>
      <img alt="PyPI - version" src="https://img.shields.io/pypi/v/mappingtools">
      <img alt="PyPI - Status" src="https://img.shields.io/pypi/status/mappingtools">
      <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/mappingtools">
      <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dd/mappingtools">
      <br>
      <img alt="GitHub" src="https://img.shields.io/github/license/erivlis/mappingtools">
      <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/erivlis/mappingtools">
      <img alt="GitHub last commit (by committer)" src="https://img.shields.io/github/last-commit/erivlis/mappingtools">
      <a href="https://github.com/erivlis/mappingtools/graphs/contributors"><img alt="Contributors" src="https://img.shields.io/github/contributors/erivlis/mappingtools.svg"></a>
    </td>
  </tr>
  <tr>
    <td>Tools</td>
    <td>
      <a href="https://www.jetbrains.com/pycharm/"><img alt="PyCharm" src="https://img.shields.io/badge/PyCharm-FCF84A.svg?logo=PyCharm&logoColor=black&labelColor=21D789&color=FCF84A"></a>
      <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;"></a>
      <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv" style="max-width:100%;"></a>
      <!-- a href="https://squidfunk.github.io/mkdocs-material/"><img src="https://img.shields.io/badge/Material_for_MkDocs-526CFE?&logo=MaterialForMkDocs&logoColor=white&labelColor=grey"></a -->
    </td>
  </tr>
  <tr>
    <td>CI/CD</td>
    <td>
      <a href="https://github.com/erivlis/mappingtools/actions/workflows/test.yml"><img alt="Tests" src="https://github.com/erivlis/mappingtools/actions/workflows/test.yml/badge.svg?branch=main"></a>
      <a href="https://github.com/erivlis/mappingtools/actions/workflows/publish.yml"><img alt="Publish" src="https://github.com/erivlis/mappingtools/actions/workflows/publish.yml/badge.svg"></a>
      <!--a href="https://github.com/erivlis/mappingtools/actions/workflows/publish-docs.yaml"><img alt="Publish Docs" src="https://github.com/erivlis/mappingtools/actions/workflows/publish-docs.yaml/badge.svg"></a-->
    </td>
  </tr>
  <tr>
    <td>Scans</td>
    <td>
      <a href="https://codecov.io/gh/erivlis/mappingtools"><img alt="Coverage" src="https://codecov.io/gh/erivlis/mappingtools/graph/badge.svg?token=POODT8M9NV"/></a>
      <br>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Quality Gate Status" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=alert_status"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Security Rating" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=security_rating"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Maintainability Rating" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=sqale_rating"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Reliability Rating" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=reliability_rating"></a>
      <br>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Lines of Code" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=ncloc"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Vulnerabilities" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=vulnerabilities"></a>
      <a href="https://sonarcloud.io/summary/new_code?id=erivlis_mappingtools"><img alt="Bugs" src="https://sonarcloud.io/api/project_badges/measure?project=erivlis_mappingtools&metric=bugs"></a>
      <br>
      <a href="https://app.codacy.com/gh/erivlis/mappingtools/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade"><img alt="Codacy Quality" src="https://app.codacy.com/project/badge/Grade/8b83a99f939b4883ae2f37d7ec3419d1"></a>
      <a href="https://app.codacy.com/gh/erivlis/mappingtools/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage"><img alt="Codacy Coverage" src="https://app.codacy.com/project/badge/Coverage/8b83a99f939b4883ae2f37d7ec3419d1"/></a>
    </td>
  </tr>
</table>

## Usage

### Transformers

#### `distinct`

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

#### `keep`

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

#### `remove`

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

#### `inverse`

Swaps keys and values in a dictionary.

```python
from mappingtools import inverse

original_mapping = {'a': {1, 2}, 'b': {3}}
inverted_mapping = inverse(original_mapping)
print(inverted_mapping)
# Output: defaultdict(<class 'set'>, {1: {'a'}, 2: {'a'}, 3: {'b'}})
```

#### `strictify`

Strictify function applies a strict structural conversion to an object using optional converters for keys and values.

```python
from mappingtools import strictify


def uppercase_key(key):
    return key.upper()


def double_value(value):
    return value * 2


data = {'a': 1, 'b': 2}
result = strictify(data, key_converter=uppercase_key, value_converter=double_value)
print(result)
# Output: {'A': 2, 'B': 4}
```

#### `simplify`

Converts objects to strictly structured dictionaries.

```python
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

from mappingtools import simplify

data = {'key1': 'value1', 'key2': ['item1', 'item2']}
simplified_data = simplify(data)
print(simplified_data)
# Output: {'key1': 'value1', 'key2': ['item1', 'item2']}

counter = Counter({'a': 1, 'b': 2})
print(counter)
# Output: Counter({'b': 2, 'a': 1})

simplified_counter = simplify(counter)
print(simplified_counter)


# Output: {'a': 1, 'b': 2}


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
# Output: SampleDataClass(a=1, b=2, aa='11', bb='22', c=[1, 2], d={'aaa': 111, 'bbb': '222'}, e=datetime.datetime(2024, 7, 22, 21, 42, 17, 314159))

simplified_sample_dataclass = simplify(sample_dataclass)
print(simplified_sample_dataclass)
# Output: {'a': 1, 'aa': '11', 'b': 2, 'bb': '22', 'c': [1, 2], 'd': {'aaa': 111, 'bbb': '222'}, 'e': datetime.datetime(2024, 7, 22, 21, 42, 17, 314159)}
```

#### `listify`

Transforms complex objects into a list of dictionaries with key and value pairs.

```python
from mappingtools import listify

wrapped_data = {'key1': {'subkey': 'value'}, 'key2': ['item1', 'item2']}
unwrapped_data = listify(wrapped_data)
print(unwrapped_data)
# Output: [{'key': 'key1', 'value': [{'key': 'subkey', 'value': 'value'}]}, {'key': 'key2', 'value': ['item1', 'item2']}]
```

### Collectors

#### `nested_defaultdict`

Creates a nested defaultdict with specified depth and factory.

```python
from mappingtools import nested_defaultdict

nested_dd = nested_defaultdict(1, list)
nested_dd[0][1].append('value')
print(nested_dd)
# Output: defaultdict(<function nested_defaultdict.<locals>.factory at ...>, {0: defaultdict(<function nested_defaultdict.<locals>.factory at ...>, {1: ['value']})})
```

#### `CategoryCounter`

The CategoryCounter class extends a dictionary to count occurrences of data items categorized by multiple categories.
It maintains a total count of all data items and allows categorization using direct values or functions.

```python
from mappingtools import CategoryCounter

counter = CategoryCounter()

for fruit in ['apple', 'banana', 'apple']:
    counter.update({fruit: 1}, type='fruit', char_count=len(fruit), unique_char_count=len(set(fruit)))

print(counter.total)
# Output: Counter({'apple': 2, 'banana': 1})

print(counter)
# Output: CategoryCounter({'type': defaultdict(<class 'collections.Counter'>, {'fruit': Counter({'apple': 2, 'banana': 1})}), 'char_count': defaultdict(<class 'collections.Counter'>, {5: Counter({'apple': 2}), 6: Counter({'banana': 1})}), 'unique_char_count': defaultdict(<class 'collections.Counter'>, {4: Counter({'apple': 2}), 3: Counter({'banana': 1})})})
```

#### `MappingCollector`

A class designed to collect key-value pairs into an internal mapping based on different modes.
It supports modes like ALL, COUNT, DISTINCT, FIRST, and LAST, each dictating how key-value pairs are
collected.

```python
from mappingtools import MappingCollector, MappingCollectorMode

collector = MappingCollector(MappingCollectorMode.ALL)
collector.add('a', 1)
collector.add('a', 2)
collector.collect([('b', 3), ('b', 4)])
print(collector.mapping)
# Output: {'a': [1, 2], 'b': [3, 4]}
```

## Development

### Ruff

```shell
ruff check src
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