from collections import Counter

import pytest

from mappingtools.collectors import CategoryCounter

fruits = ['apple', 'apricot', 'banana', 'cherry', 'pear', 'pineapple', 'plum', 'banana']

# Expected counts per category value
expected_char_count = {
    4: Counter({'pear': 1, 'plum': 1}),
    5: Counter({'apple': 1}),
    6: Counter({'banana': 2, 'cherry': 1}),
    7: Counter({'apricot': 1}),
    9: Counter({'pineapple': 1}),
}

expected_unique_char_count = {
    3: Counter({'banana': 2}),
    4: Counter({'apple': 1, 'pear': 1, 'plum': 1}),
    5: Counter({'cherry': 1}),
    6: Counter({'pineapple': 1}),
    7: Counter({'apricot': 1}),
}


# Initialize CategoryCounter and collect a list of items
def test_initialize_and_collect_list():
    # Arrange
    counter = CategoryCounter()

    # Act
    # We collect without categories to see if it runs,
    # but without categories, CategoryCollector doesn't store anything
    # (unless we had a default category, which we don't).
    # The original test checked 'total', which is gone.
    # So we'll just check that it doesn't crash.
    counter.collect(fruits)

    # Assert
    # No categories defined, so the counter should be empty
    assert len(counter) == 0


# Categorize items using direct category values
def test_categorize_with_direct_category_values():
    # Arrange
    counter = CategoryCounter()

    # Act
    for fruit in fruits:
        # New API: add(item, category=val)
        counter.add(fruit, char_count=len(fruit), unique_char_count=len(set(fruit)))

    # Assert
    # Access via .mapping because MappingCollector is not subscriptable
    assert counter['char_count'].mapping == expected_char_count
    assert counter['unique_char_count'].mapping == expected_unique_char_count


# Categorize items using functions to determine categories
def test_categorize_with_functions():
    # Arrange
    counter = CategoryCounter()

    # Act
    # New API: collect(iterable, category=func)
    # The function receives the ITEM, not a batch.
    counter.collect(fruits, char_count=len, unique_char_count=lambda s: len(set(s)))

    # Assert
    assert counter['char_count'].mapping == expected_char_count
    assert counter['unique_char_count'].mapping == expected_unique_char_count


# Retrieve counts for specific categories
def test_retrieve_counts_for_specific_categories():
    # Arrange
    counter = CategoryCounter()
    # Expected for 'fruit' category (all items)
    expected = Counter(fruits)

    # Act
    counter.collect(fruits, type='fruit')

    # Assert
    # counter['type'] is a MappingCollector
    # counter['type'].mapping is a dict-like of Counters
    # Since we used a constant category 'fruit', all items are in that bucket.
    assert counter['type'].mapping['fruit'] == expected


# Collect with an empty list
def test_collect_with_empty_list():
    # Arrange
    counter = CategoryCounter()

    # Act
    counter.collect([])

    # Assert
    assert len(counter) == 0


# Provide static category
def test_categories_not_matching_any_items():
    # Arrange
    counter = CategoryCounter()

    # Act
    counter.collect(fruits, type='fruit')

    # Assert
    # 'car' category value was never used
    assert 'car' not in counter['type'].mapping


# Update with mixed data types
def test_collect_with_mixed_data_types():
    # Arrange
    counter = CategoryCounter()
    data = ['apple', 1, 2.5, 1, 1]

    # Act
    # We need a category to store them
    counter.collect(data, type='mixed')

    # Assert
    expected = Counter({'apple': 1, 1: 3, 2.5: 1})
    assert counter['type'].mapping['mixed'] == expected


# Verify initialization without any updates
def test_initialization_without_updates():
    # Arrange & Act
    counter = CategoryCounter()

    # Assert
    assert len(counter) == 0


# Check behavior with nested data structures (unhashable)
def test_nested_data_structures_behavior():
    # Arrange
    counter = CategoryCounter()
    data = [{'name': 'apple'}, {'name': 'banana'}, {'name': 'apple'}]

    # Act & Assert
    # Counter keys must be hashable. Dicts are not.
    with pytest.raises(TypeError):
        counter.collect(data, type='dict')


# Correctly formats the string representation of CategoryCounter
def test_correct_formatting():
    # Arrange
    counter = CategoryCounter()

    # Act
    result = repr(counter)

    # Assert
    # The new repr includes aggregation and mapping
    # "CategoryCollector(aggregation=Aggregation.COUNT, mapping={})"
    # Note: CategoryCounter inherits CategoryCollector's repr
    assert 'CategoryCollector' in result
    assert 'Aggregation.COUNT' in result
    assert 'mapping={}' in result


# Test invalid category type in add (Coverage)
def test_add_invalid_category_type():
    # Arrange
    counter = CategoryCounter()

    # Act & Assert
    with pytest.raises(TypeError, match='Invalid category type'):
        # Pass a list as a category value (unhashable/invalid)
        counter.add('item', bad_cat=['invalid'])


# Test invalid category type in collect fast path (Coverage)
def test_collect_invalid_category_type_fast_path():
    # Arrange
    counter = CategoryCounter()

    # Act & Assert
    with pytest.raises(TypeError, match='Invalid category type'):
        # Pass a list as a category value in collect (constant category)
        counter.collect(['item'], bad_cat=['invalid'])
