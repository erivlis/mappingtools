from collections import Counter
from collections.abc import Callable, MutableMapping
from dataclasses import dataclass
from enum import Enum
from typing import Any


def first_aggregator(mapping, key, value):
    if key not in mapping:
        mapping[key] = value


class Aggregation(Enum):
    @dataclass(frozen=True)
    class Item:
        collection_type: type | None
        func: Callable[[MutableMapping, Any, Any], None]

    """
    Define an enumeration class for data aggregation modes.

    Attributes:
        ALL: Collect all values (list).
        COUNT: Count the occurrences of each value.
        DISTINCT: Collect distinct values (set).
        FIRST: Collect the first value encountered.
        LAST: Collect the last value encountered.
        SUM: Sum all values.
        MAX: Maximum value.
        MIN: Minimum value.
        RUNNING_AVERAGE: Calculate a running average.
    """
    ALL = Item(collection_type=list, func=lambda mapping, key, value: mapping[key].append(value))
    COUNT = Item(collection_type=Counter, func=lambda mapping, key, value: mapping[key].update({value: 1}))
    DISTINCT = Item(collection_type=set, func=lambda mapping, key, value: mapping[key].add(value))
    FIRST = Item(collection_type=None, func=first_aggregator)
    LAST = Item(collection_type=None, func=lambda mapping, key, value: mapping.__setitem__(key, value))
    SUM = Item(
        collection_type=float, func=lambda mapping, key, value: mapping.__setitem__(key, mapping.get(key, 0) + value)
    )
    MAX = Item(
        collection_type=float,
        func=lambda mapping, key, value: mapping.__setitem__(key, max(mapping.get(key, value), value)),
    )
    MIN = Item(
        collection_type=float,
        func=lambda mapping, key, value: mapping.__setitem__(key, min(mapping.get(key, value), value)),
    )
    RUNNING_AVERAGE = Item(
        collection_type=float,
        func=lambda mapping, key, value: mapping.__setitem__(key, (mapping.get(key, 0) + value) / 2),
    )

    @property
    def collection_type(self) -> type | None:
        """
        Return the collection type used for this aggregation mode.
        """
        return self.value.collection_type

    @property
    def aggregator(self) -> Callable[[MutableMapping, Any, Any], None]:
        """
        Return a specialized aggregator function for this mode.
        """
        return self.value.func
