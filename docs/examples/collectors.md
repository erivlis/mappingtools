---
icon: lucide/square-sigma
---

# Collectors

!!! Abstract
    Collectors are classes that collect data items into a Mapping.

## AutoMapper

A Mapping that automatically generates and assigns unique, minified string values for any new keys accessed.
The values are generated using the specified alphabet.

<!-- name: test_auto_mapper -->

```python linenums="1"
from mappingtools.collectors import AutoMapper

auto_mapper = AutoMapper()
print(auto_mapper['example_key'])
print(auto_mapper['another_key'])
print(auto_mapper['example_key'])
auto_mapper
# output:
# 'A'
# 'B'
# 'A'
# AutoMapper({'example_key': 'A', 'another_key': 'B'})
greek_auto_mapper = AutoMapper(alphabet='αβγ')
print(greek_auto_mapper['first'])
print(greek_auto_mapper['second'])
print(greek_auto_mapper['first'])
print(greek_auto_mapper['third'])
print(greek_auto_mapper['fourth'])
print(greek_auto_mapper['fifth'])
greek_auto_mapper
# output:
# 'α'
# 'β'
# 'γ'
# 'αα'
# 'αβ'
# AutoMapper({'first': 'α', 'second': 'β', 'third': 'γ', 'fourth': 'αα', 'fifth': 'αβ'})
```

## CategoryCounter

The CategoryCounter class extends a dictionary to count occurrences of data items categorized by multiple categories.
It maintains a total count of all data items and allows categorization using direct values or functions.

<!-- name: test_category_counter -->

```python linenums="1"
from mappingtools.collectors import CategoryCounter

counter = CategoryCounter()

for fruit in ['apple', 'banana', 'apple']:
    counter.update({fruit: 1}, type='fruit', char_count=len(fruit), unique_char_count=len(set(fruit)))

print(counter.total)
# Output: Counter({'apple': 2, 'banana': 1})

print(counter)
# output: CategoryCounter({'type': defaultdict(<class 'collections.Counter'>, {'fruit': Counter({'apple': 2, 'banana': 1})}), 'char_count': defaultdict(<class 'collections.Counter'>, {5: Counter({'apple': 2}), 6: Counter({'banana': 1})}), 'unique_char_count': defaultdict(<class 'collections.Counter'>, {4: Counter({'apple': 2}), 3: Counter({'banana': 1})})})
```

## MappingCollector

A class designed to collect key-value pairs into an internal mapping based on different modes.
It supports modes like ALL, COUNT, DISTINCT, FIRST, and LAST, each dictating how key-value pairs are
collected.

<!-- name: test_mapping_collector -->

```python linenums="1"
from mappingtools.collectors import MappingCollector, MappingCollectorMode

collector = MappingCollector(MappingCollectorMode.ALL)
collector.add('a', 1)
collector.add('a', 2)
collector.collect([('b', 3), ('b', 4)])
print(collector.mapping)
# output: {'a': [1, 2], 'b': [3, 4]}
```

## MeteredDict

A dictionary that tracks changes made to it.

<!-- name: test_metered_dict -->

```python linenums="1"
from mappingtools.collectors import MeteredDict

metered_dict = MeteredDict()
metered_dict['a'] = 1
metered_dict['b'] = 2
_ = metered_dict['a']

metered_dict
# output: {'a': 1, 'b': 2}

metered_dict.summaries()
# output: {'a': {'get': {'count': 1, 'first': datetime.datetime(2025, 10, 26, 9, 3, 52, 347825, tzinfo=datetime.timezone.utc), 'last': datetime.datetime(2025, 10, 26, 9, 3, 52, 347825, tzinfo=datetime.timezone.utc), 'duration': datetime.timedelta(0), 'frequency': 0.0}, 'get_default': {'count': 0, 'first': None, 'last': None, 'duration': datetime.timedelta(0), 'frequency': 0.0}, 'set': {'count': 1, 'first': datetime.datetime(2025, 10, 26, 9, 3, 52, 347806, tzinfo=datetime.timezone.utc), 'last': datetime.datetime(2025, 10, 26, 9, 3, 52, 347806, tzinfo=datetime.timezone.utc), 'duration': datetime.timedelta(0), 'frequency': 0.0}, 'set_default': {'count': 0, 'first': None, 'last': None, 'duration': datetime.timedelta(0), 'frequency': 0.0}, 'pop': {'count': 0, 'first': None, 'last': None, 'duration': datetime.timedelta(0), 'frequency': 0.0}}, 'b': {'get': {'count': 0, 'first': None, 'last': None, 'duration': datetime.timedelta(0), 'frequency': 0.0}, 'get_default': {'count': 0, 'first': None, 'last': None, 'duration': datetime.timedelta(0), 'frequency': 0.0}, 'set': {'count': 1, 'first': datetime.datetime(2025, 10, 26, 9, 3, 52, 347820, tzinfo=datetime.timezone.utc), 'last': datetime.datetime(2025, 10, 26, 9, 3, 52, 347820, tzinfo=datetime.timezone.utc), 'duration': datetime.timedelta(0), 'frequency': 0.0}, 'set_default': {'count': 0, 'first': None, 'last': None, 'duration': datetime.timedelta(0), 'frequency': 0.0}, 'pop': {'count': 0, 'first': None, 'last': None, 'duration': datetime.timedelta(0), 'frequency': 0.0}}}
```

## nested_defaultdict

Creates a nested defaultdict with specified depth and factory.

<!-- name: test_nested_defaultdict -->

```python linenums="1"
from mappingtools.collectors import nested_defaultdict

nested_dd = nested_defaultdict(1, list)
nested_dd[0][1].append('value')
print(nested_dd)
# output: defaultdict(<function nested_defaultdict.<locals>.factory at ...>, {0: defaultdict(<function nested_defaultdict.<locals>.factory at ...>, {1: ['value']})})
```
