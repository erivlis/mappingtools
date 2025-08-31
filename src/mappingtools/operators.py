import itertools
import math
import string
from collections import defaultdict
from collections.abc import Callable, Generator, Iterable, Mapping
from itertools import chain
from typing import Any

from mappingtools._tools import _is_strict_iterable
from mappingtools.typing import K


def _take(keys: Iterable[K], mapping: Mapping[K, Any], exclude: bool = False) -> dict[K, Any]:
    """
    Return a dictionary pertaining to the specified keys and their corresponding values from the mapping.

    Args:
        keys (Iterable[K]): The keys to include in the resulting dictionary.
        mapping (Mapping[K, Any]): The mapping to extract key-value pairs from.
        exclude (bool, optional): If True, exclude the specified keys from the mapping. Defaults to False.

    Returns:
        dict[K, Any]: A dictionary with the selected keys and their values from the mapping.
    """

    if not isinstance(mapping, Mapping):
        raise TypeError(f"Parameter 'mapping' should be of type 'Mapping', but instead is type '{type(mapping)}'")

    mapping_keys = set(mapping.keys())
    keys = set(keys) & mapping_keys  # intersection with keys to get actual existing keys
    if exclude:
        keys = mapping_keys - keys

    return {k: mapping.get(k) for k in keys}


def keep(keys: Iterable[K], *mappings: Mapping[K, Any]) -> Generator[Mapping[K, Any], Any, None]:
    """
    Yield a subset of mappings by keeping only the specified keys.

    Args:
        keys (Iterable[K]): The keys to keep in the mappings.
        *mappings (Mapping[K, Any]): Variable number of mappings to filter.

    Yields:
        Generator[Mapping[K, Any], Any, None]: A generator of mappings with only the specified keys.
    """
    yield from (_take(keys, mapping) for mapping in mappings)


def remove(keys: Iterable[K], *mappings: Mapping[K, Any]) -> Generator[Mapping[K, Any], Any, None]:
    """
    Yield a subset of mappings by removing the specified keys.

    Args:
        keys (Iterable[K]): The keys to remove from the mappings.
        *mappings (Mapping[K, Any]): Variable number of mappings to filter.

    Yields:
        Generator[Mapping[K, Any], Any, None]: A generator of mappings with specified keys removed.
    """
    yield from (_take(keys, mapping, exclude=True) for mapping in mappings)


def distinct(key: K, *mappings: Mapping[K, Any]) -> Generator[Any, Any, None]:
    """
    Yield distinct values for the specified key across multiple mappings.

    Args:
        key (K): The key to extract distinct values from the mappings.
        *mappings (Mapping[K, Any]): Variable number of mappings to search for distinct values.

    Yields:
        Generator[K, Any, None]: A generator of distinct values extracted from the mappings.
    """
    distinct_value_type_pairs = set()
    for mapping in mappings:
        value = mapping.get(key)
        value_type_pair = (value, type(value))
        if key in mapping and value_type_pair not in distinct_value_type_pairs:
            distinct_value_type_pairs.add(value_type_pair)
            yield value


def inverse(mapping: Mapping[Any, set]) -> Mapping[Any, set]:
    """
    Return a new dictionary with keys and values swapped from the input mapping.

    Args:
        mapping (Mapping[Any, set]): The input mapping to invert.

    Returns:
        Mapping: A new Mapping with values as keys and keys as values.
    """
    items = chain.from_iterable(((vi, k) for vi in v) for k, v in mapping.items())
    dd = defaultdict(set)
    for k, v in items:
        dd[k].add(v)

    return dd


def flattened(mapping: Mapping[Any, Any]) -> dict[tuple, Any]:
    """
    Flatten a nested mapping structure into a single-level dictionary.

    :param mapping: A nested mapping structure to be flattened.
    :return: A dictionary representing the flattened structure.
    """

    def flatten(key: tuple, value: Any):
        if isinstance(value, Mapping):
            for k, v in value.items():
                new_key = tuple([*key, *k] if _is_strict_iterable(k) else [*key, k])
                yield from flatten(new_key, v)
        else:
            yield key, value

    return dict(flatten((), mapping))


def stream(mapping: Mapping, item_factory: Callable[[Any, Any], Any] | None = None) -> Generator[Any, Any, None]:
    """
    Generate a stream of items from a mapping.

    Args:
        mapping (Mapping): The mapping object to stream items from.
        item_factory (Callable[[Any, Any], Any], optional): A function that transforms each key-value pair from
            the mapping. Defaults to None.

    Yields:
        The streamed items from the mapping.
    """

    items = mapping.items() if item_factory is None else iter(item_factory(k, v) for k, v in mapping.items())
    yield from items


def stream_dict_records(mapping: Mapping,
                        key_name: str = 'key',
                        value_name: str = 'value') -> Generator[Mapping[str, Any], Any, None]:
    """
    Generate dictionary records from a mapping.

    Args:
        mapping (Mapping): The input mapping to generate records from.
        key_name (str): The name to use for the key in the generated records. Defaults to 'key'.
        value_name (str): The name to use for the value in the generated records. Defaults to 'value'.

    Yields:
        dictionary records based on the input mapping.
    """

    def record(k, v):
        return {key_name: k, value_name: v}

    yield from stream(mapping, record)


class StringArrangements:
    """
    A string arrangement is a permutation with repetition of characters taken from the alphabet.
    The ordinality of the generated strings is determined by the ordinality expressed by the characters'
    order within the input alphabet.
    """

    @classmethod
    def ascii_uppercase(cls):
        return cls(string.ascii_uppercase)

    @classmethod
    def ascii_lowercase(cls):
        return cls(string.ascii_lowercase)

    @classmethod
    def ascii_letters(cls):
        return cls(string.ascii_letters)

    @classmethod
    def ascii_digits(cls):
        return cls(string.digits)

    @classmethod
    def hex_digits(cls):
        return cls(string.hexdigits)

    @classmethod
    def oct_digits(cls):
        return cls(string.octdigits)

    def __init__(self, alphabet: str = string.ascii_uppercase):
        self.alphabet = alphabet

    def count_of(self, word_length: int) -> int:
        return len(self.alphabet) ** word_length

    def of(self, length: int) -> Generator[str, None, None]:
        """
        Generates all possible string arrangements of a given length using the defined alphabet.

        Args:
            length (int): The length of the strings to generate.

        Yields:
            Generator[str]: A generator of strings.

        Raises:
            ValueError: if length is not a positive integer.
        """
        if length <= 0:
            raise ValueError("'length' must be greater than 0.")
        for s in itertools.product(self.alphabet, repeat=length):
            yield ''.join(s)

    def stream(self, count: int) -> Generator[str, None, None]:
        """
        Generates the given count of possible string arrangements with all lengths.
        Starting with length 1 then if possible 2 .

        Args:
            count (int): The number of strings to generate.

        Yields:
            Generator[str]: A generator of strings.

        Raises:
            ValueError: if count is not a positive integer.

        """
        if count <= 0:
            raise ValueError("'count' must be greater than 0.")

        _length: int = 1
        _count: int = 0
        while True:
            for s in self.of(_length):
                yield s
                _count += 1
                if _count >= count:
                    break
            _length += 1


def probabilities(length: int,
                  alphabet: str = string.ascii_uppercase,
                  distribution: Callable[[str], float] | None = None):
    """
    Generate probabilities for all possible string arrangements of a given length using the defined alphabet.

    Args:
        length (int): The length of the strings to generate.
        alphabet (str): The alphabet to use for generating strings. Defaults to string.ascii_uppercase.
        distribution (Callable[[str], float] | None, optional): A function that takes a string and returns its
            probability. If None, a uniform distribution is assumed. Defaults to None.

    Yields:
        Generator[float]: A generator of probabilities for each string arrangement.
    """
    if distribution is None or not callable(distribution):
        alphabet_length = len(alphabet)

        def p(_):
            return alphabet_length ** -length

        distribution = p

    for x in StringArrangements(alphabet).of(length):
        yield distribution(x)


def shannon_entropy(length: int, alphabet: str = string.ascii_uppercase,
                    distribution: Callable[[str], float] | None = None):
    """
    Calculate the Shannon entropy for all possible string arrangements of a given length using the defined alphabet.
    Args:
        length: int - The length of the strings to generate.
        alphabet: str - The alphabet to use for generating strings. Defaults to string.ascii_uppercase.
        distribution: Callable[[str], float] | None - A function that takes a string and returns its probability.
            If None, a uniform distribution is assumed. Defaults to None.

    Returns:
        float: The Shannon entropy of the string arrangements.
    """
    return -sum(p * math.log(p) for p in probabilities(length, alphabet, distribution))


def unique_strings(alphabet: str = string.ascii_uppercase, string_length: int = 0) -> Generator[Any, Any, None]:
    """Generates a stream of the strings using the given alphabet and string_length.
       If string_length=0 (the default), the stream will be **infinite**, and consist of all string lengths.

    Args:
        alphabet (str): The alphabet to use for generating strings. Defaults to string.ascii_uppercase.
        string_length (int, optional): The length of the strings to generate. Defaults to 0. If string_length is 0,
            the generator will start with strings of length 1 and increase the lengths indefinitely.

    Yields:
        str: The generated strings.
    """

    string_arrangements = StringArrangements(alphabet)

    if string_length > 0:
        yield from string_arrangements.of(string_length)
    else:
        _length = 1
        while True:
            yield from string_arrangements.of(_length)
            _length += 1


__all__ = ['distinct', 'flattened', 'inverse', 'keep', 'remove', 'stream', 'stream_dict_records', 'unique_strings']
