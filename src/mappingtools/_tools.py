import dataclasses
import itertools
import math
import string
from collections.abc import Callable, Generator, Iterable, Mapping
from typing import Any


def _is_strict_iterable(obj: Iterable) -> bool:
    return isinstance(obj, Iterable) and not isinstance(obj, str | bytes | bytearray)


def _is_class_instance(obj) -> bool:
    return (dataclasses.is_dataclass(obj) and not isinstance(obj, type)) or hasattr(obj, '__dict__')


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
        _continue = True
        while _continue:
            for s in self.of(_length):
                yield s
                _count += 1
                if _count >= count:
                    _continue = False
                    break
            _length += 1

    def uniform_distribution_of(self, length: int) -> Callable[[str], float]:
        """
        Create a uniform distribution function for all possible string arrangements of a given length using the defined
        alphabet
        """

        uniform_probability = len(self.alphabet) ** -length

        def uniform_distribution(_: Any):
            return uniform_probability

        return uniform_distribution

    def weighted_distribution_of(self,
                                 length,
                                 weights: Mapping[str, float],
                                 distribution: Callable[[str], float] | None = None) -> Callable[[str], float]:
        """
        Create a weighted distribution function for all possible string arrangements of a given length using the defined
        alphabet and the provided word weights.
        """
        distribution = distribution or self.uniform_distribution_of(length)

        _total_weight = sum(weights.values())
        if _total_weight <= 0:
            raise ValueError("Total weight must be greater than 0.")

        # _normalized_weights = {k: v / _total_weight for k, v in weights.items()}

        def weighted_distribution(s: str):
            w = weights.get(s, 0)
            return _total_weight * distribution(s) * w if w > 0 else 0.0

        return weighted_distribution


def probabilities(length: int,
                  alphabet: str = string.ascii_uppercase,
                  distribution: Callable[[str], float] | None = None,
                  weights: Mapping[str, float] | None = None) -> Generator[float, None, None]:
    """
    Generate probabilities for all possible string arrangements of a given length using the defined alphabet.

    Args:
        length (int): The length of the strings to generate.
        alphabet (str): The alphabet to use for generating strings. Defaults to string.ascii_uppercase.
        distribution (Callable[[str], float] | None, optional): A function that takes a string and returns its
            probability. If None, a uniform distribution is assumed. Defaults to None.
        weights (Mapping[str, float] | None, optional): A mapping of string arrangements to their weights.
            If provided, a weighted distribution is created using these weights. Defaults to None.

    Yields:
        Generator[float]: A generator of probabilities for each string arrangement.
    """
    string_arrangements = StringArrangements(alphabet)

    if weights is None and distribution is None:
        distribution = string_arrangements.uniform_distribution_of(length)
    elif weights is not None:
        distribution = string_arrangements.weighted_distribution_of(length, weights, distribution)

    for x in string_arrangements.of(length):
        yield distribution(x)


def shannon_entropy(length: int,
                    alphabet: str = string.ascii_uppercase,
                    distribution: Callable[[str], float] | None = None,
                    weights: Mapping[str, float] | None = None) -> float:
    """
    Calculate the Shannon entropy for all possible string arrangements of a given length using the defined alphabet.
    Args:
        length: int - The length of the strings to generate.
        alphabet: str - The alphabet to use for generating strings. Defaults to string.ascii_uppercase.
        distribution: Callable[[str], float] | None - A function that takes a string and returns its probability.
            If None, a uniform distribution is assumed. Defaults to None.
        weights: Mapping[str, float] | None - A mapping of string arrangements to their weights.
            If provided, a weighted distribution is created using these weights. Defaults to None.

    Returns:
        float: The Shannon entropy of the string arrangements.
    """
    return -sum(p * math.log(p) for p in probabilities(length, alphabet, distribution, weights))


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
