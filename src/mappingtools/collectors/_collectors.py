import string
from collections import Counter, defaultdict
from collections.abc import Callable, Mapping
from typing import Any

from mappingtools._tools import unique_strings
from mappingtools.typing import Category


class CategoryCounter(dict[str, defaultdict[Category, Counter]]):

    def __init__(self):
        super().__init__()
        self.total = Counter()

    def __repr__(self):
        return f"CategoryCounter({super().__repr__()})"

    def update(self, data, **categories: Category | Callable[[Any], Category]):
        """
        Updates a CategoryCounter object with data and corresponding categories.

        Parameters:
            data: Any - The data to update the counter with (see Counter update method documentation).
            **categories: Category | Callable[[Any], Category] - categories to associate the data with.
                The categories can be either a direct value or a function that extracts the category from the data.

        Returns:
            None
        """
        self.total.update(data)
        for category_name, category_value in categories.items():
            category_value = category_value(data) if callable(category_value) else category_value
            if category_name not in self:
                self[category_name] = defaultdict(Counter)
            self[category_name][category_value].update(data)


class AutoMapper(Mapping):
    """
    A Mapping that automatically generates and assigns unique, minified strings
    for any new keys accessed. The minified keys are generated using the specified alphabet.

    Args:
        alphabet: str - The alphabet to use for generating minified keys. Default is uppercase ASCII
          letters (A-Z).

    Example:
        >>> from mappingtools.collectors import AutoMapper
        >>> auto_mapper = AutoMapper()
        >>> auto_mapper['example_key']
        'A'
        >>> auto_mapper['another_key']
        'B'
        >>> auto_mapper['example_key']
        'A'
        >>> auto_mapper
        {'example_key': 'A', 'another_key': 'B'}
    """

    def __init__(self, alphabet: str = string.ascii_uppercase):
        self._us = unique_strings(alphabet)

        def _next_key():
            return next(self._us)

        self._mapping = defaultdict(_next_key)

    def __getitem__(self, item):
        return self._mapping[item]

    def __iter__(self):
        return iter(self._mapping)

    def __len__(self):
        return len(self._mapping)

    def __repr__(self):
        return f"{self.__class__.__name__}({dict(self._mapping)})"

    def __str__(self):
        return repr(self)


def nested_defaultdict(nesting_depth: int = 0, default_factory: Callable | None = None, **kwargs) -> defaultdict:
    """Return a nested defaultdict with the specified nesting depth and default factory.
    A nested_defaultdict with nesting_depth=0 is equivalent to builtin 'collections.defaultdict'.
    For each increment in nesting_depth an additional item accessor is added.

    Args:
        nesting_depth (int): The depth of nesting for the defaultdict (default is 0);
        default_factory (Callable): The default factory function for the defaultdict (default is None).
        **kwargs: Additional keyword arguments to initialize the most nested defaultdict.

    Returns:
        defaultdict: A nested defaultdict based on the specified parameters.
    """

    if nesting_depth < 0:
        raise ValueError("'nesting_depth' must be zero or more.")

    if default_factory is not None and not callable(default_factory):
        raise TypeError("default_factory argument must be Callable or None")

    def factory():
        if nesting_depth > 0:
            return nested_defaultdict(nesting_depth=nesting_depth - 1, default_factory=default_factory, **kwargs)
        else:
            return default_factory() if default_factory else None

    return defaultdict(factory, **kwargs)
