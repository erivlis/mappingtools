import string
from collections import defaultdict
from collections.abc import Callable, Mapping

from mappingtools._tools import unique_strings


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
        return f'{self.__class__.__name__}({dict(self._mapping)})'

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
        raise TypeError('default_factory argument must be Callable or None')

    def factory():
        if nesting_depth > 0:
            return nested_defaultdict(nesting_depth=nesting_depth - 1, default_factory=default_factory, **kwargs)
        else:
            return default_factory() if default_factory else None

    return defaultdict(factory, **kwargs)
