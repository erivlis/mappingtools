import itertools
import string

from mappingtools._tools import unique_strings


# Generates strings of length 1 using default uppercase alphabet when no parameters are provided
def test_default_parameters_generates_length_1_uppercase():
    # Arrange

    expected_first_strings = ['A', 'B', 'C', 'D', 'E']

    # Act
    generator = unique_strings()
    result = [next(generator) for _ in range(5)]

    # Assert
    assert all(len(s) == 1 for s in result)
    assert all(s in string.ascii_uppercase for s in result)
    assert result == expected_first_strings


# Generates strings of specified length using default alphabet when only string_length is provided
def test_specified_length_with_default_alphabet():
    # Arrange
    length = 2
    expected_first_strings = ['AA', 'AB', 'AC', 'AD', 'AE']

    # Act
    generator = unique_strings(string_length=length)
    result = [next(generator) for _ in range(5)]

    # Assert
    assert all(len(s) == length for s in result)
    assert all(all(char in string.ascii_uppercase for char in s) for s in result)
    assert result == expected_first_strings


# Generates strings using custom alphabet when alphabet parameter is provided
def test_custom_alphabet():
    # Arrange
    custom_alphabet = "123"
    length = 1
    expected_strings = ['1', '2', '3']

    # Act
    generator = unique_strings(alphabet=custom_alphabet, string_length=length)
    result = list(generator)

    # Assert
    assert all(len(s) == length for s in result)
    assert all(all(char in custom_alphabet for char in s) for s in result)
    assert result == expected_strings


# Yields all possible combinations for a given alphabet and length
def test_all_possible_combinations():
    # Arrange
    alphabet = "abc"
    length = 2
    expected_count = len(alphabet) ** length  # 3^2 = 9 combinations
    expected_combinations = ['aa', 'ab', 'ac', 'ba', 'bb', 'bc', 'ca', 'cb', 'cc']

    # Act
    generator = unique_strings(alphabet=alphabet, string_length=length)
    result = list(generator)

    # Assert
    assert len(result) == expected_count
    assert sorted(result) == sorted(expected_combinations)


# Correctly increments string length when string_length=0
def test_increments_string_length():
    # Arrange
    alphabet = "ab"

    # Act
    generator = unique_strings(alphabet=alphabet, string_length=0)

    # Get all length 1 strings
    length_1_strings = [next(generator) for _ in range(len(alphabet))]

    # Get first length 2 string
    first_length_2_string = next(generator)

    # Assert
    assert all(len(s) == 1 for s in length_1_strings)
    assert sorted(length_1_strings) == ['a', 'b']
    assert len(first_length_2_string) == 2
    assert first_length_2_string == 'aa'


# Empty alphabet parameter should yield no strings
def test_empty_alphabet_yields_no_strings():
    # Arrange
    empty_alphabet = ""

    # Act
    generator = unique_strings(alphabet=empty_alphabet, string_length=1)

    # Assert
    # Should yield no strings, so next() should raise StopIteration
    import pytest
    with pytest.raises(StopIteration):
        next(generator)


# Very large string_length value handling
def test_large_string_length():
    # Arrange
    alphabet = "a"
    large_length = 100

    # Act
    generator = unique_strings(alphabet=alphabet, string_length=large_length)
    result = next(generator)

    # Assert
    assert len(result) == large_length
    assert result == "a" * large_length


# Single character alphabet generates repeated character strings
def test_single_character_alphabet():
    # Arrange
    alphabet = "x"
    length = 3

    # Act
    generator = unique_strings(alphabet=alphabet, string_length=length)
    result = list(generator)

    # Assert
    assert len(result) == 1
    assert result[0] == "xxx"


# Non-ASCII characters in alphabet parameter
def test_non_ascii_characters():
    # Arrange
    alphabet = "αβγ"  # Greek letters
    length = 1
    expected_strings = ['α', 'β', 'γ']

    # Act
    generator = unique_strings(alphabet=alphabet, string_length=length)
    result = list(generator)

    # Assert
    assert result == expected_strings


# Handling string_length=0 (default) with infinite generation
def test_infinite_generation():
    # Arrange
    alphabet = "ab"
    expected_length_1 = ['a', 'b']
    expected_length_2 = ['aa', 'ab', 'ba', 'bb']

    # Act
    generator = unique_strings(alphabet=alphabet)

    # Get all length 1 strings
    length_1_strings = [next(generator) for _ in range(len(alphabet))]

    # Get all length 2 strings
    length_2_strings = [next(generator) for _ in range(len(alphabet) ** 2)]

    # Assert
    assert sorted(length_1_strings) == expected_length_1
    assert sorted(length_2_strings) == expected_length_2


# Memory usage increases with larger string_length values
def test_memory_usage_with_large_length():
    # Arrange
    import sys
    alphabet = "ab"
    small_length = 5
    large_length = 1000

    # Act
    small_generator = unique_strings(alphabet=alphabet, string_length=small_length)
    large_generator = unique_strings(alphabet=alphabet, string_length=large_length)

    small_string = next(small_generator)
    large_string = next(large_generator)

    small_size = sys.getsizeof(small_string)
    large_size = sys.getsizeof(large_string)

    # Assert
    assert large_size > small_size
    assert len(large_string) == large_length
    assert len(small_string) == small_length


# Performance degrades exponentially with alphabet size and string_length
def test_performance_degradation():
    # Arrange
    import time

    small_alphabet = "ab"
    large_alphabet = "abcdefghij"
    length = 4

    # Act
    # Measure time for small alphabet
    start_time = time.time()
    small_generator = unique_strings(alphabet=small_alphabet, string_length=length)
    list(small_generator)  # Consume all items
    small_time = time.time() - start_time

    # Measure time for large alphabet
    start_time = time.time()
    large_generator = unique_strings(alphabet=large_alphabet, string_length=length)
    list(large_generator)  # Consume all items
    large_time = time.time() - start_time

    # Assert
    # Large alphabet should take significantly more time
    assert large_time > small_time

    # The ratio should be roughly proportional to the difference in combinations
    # (len(large_alphabet)/len(small_alphabet))^length
    actual_ratio = large_time / small_time if small_time > 0 else float('inf')

    # Allow for some variance in timing
    assert actual_ratio > 1.0, "Large alphabet should be slower"


def test_unique_strings_finite_and_infinite_take_some():
    # Arrange

    # Act
    gen = unique_strings("AB", string_length=2)
    finite = list(gen)

    gen_inf = unique_strings("AB", string_length=0)
    taken = list(itertools.islice(gen_inf, 5))

    # Assert
    assert finite == ["AA", "AB", "BA", "BB"]
    assert taken == ["A", "B", "AA", "AB", "BA"]
