from collections import Counter
from collections.abc import Callable, Iterable, MutableMapping
from dataclasses import dataclass
from enum import Enum
from typing import Any


def all_aggregator(mapping: MutableMapping, key: Any, values: Iterable[Any]):
    """Extends the list at mapping[key] with values."""
    mapping[key].extend(values)


def count_aggregator(mapping: MutableMapping, key: Any, values: Iterable[Any]):
    """Updates the Counter at mapping[key] with values."""
    mapping[key].update(values)


def distinct_aggregator(mapping: MutableMapping, key: Any, values: Iterable[Any]):
    """Updates the set at mapping[key] with values."""
    mapping[key].update(values)


def first_aggregator(mapping: MutableMapping, key: Any, values: Iterable[Any]):
    """Sets mapping[key] to the first value if the key does not exist."""
    if key not in mapping:
        # Take the first value from the iterable
        mapping[key] = next(iter(values))


def last_aggregator(mapping: MutableMapping, key: Any, values: Iterable[Any]):
    """Sets mapping[key] to the last value in the iterable."""
    # Take the last value from the iterable
    # Efficient for sequences, less so for generic iterables without len
    val = None
    for val in values:
        pass
    mapping[key] = val


def sum_aggregator(mapping: MutableMapping, key: Any, values: Iterable[Any]):
    """Adds the sum of values to mapping[key]."""
    mapping[key] = mapping.get(key, 0) + sum(values)


def max_aggregator(mapping: MutableMapping, key: Any, values: Iterable[Any]):
    """Updates mapping[key] to the maximum of its current value and the max of values."""
    # We need to handle the case where values is an iterator (consumable)
    # and where the key might not exist yet.
    if not isinstance(values, (list, tuple)):
        values = tuple(values)

    if not values:
        return

    current = mapping.get(key)
    batch_max = max(values)

    if current is None:
        mapping[key] = batch_max
    else:
        mapping[key] = max(current, batch_max)


def min_aggregator(mapping: MutableMapping, key: Any, values: Iterable[Any]):
    """Updates mapping[key] to the minimum of its current value and the min of values."""
    if not isinstance(values, (list, tuple)):
        values = tuple(values)

    if not values:
        return

    current = mapping.get(key)
    batch_min = min(values)

    if current is None:
        mapping[key] = batch_min
    else:
        mapping[key] = min(current, batch_min)


def ema_aggregator(mapping: MutableMapping, key: Any, values: Iterable[Any]):
    """Updates mapping[key] to the exponential moving average (alpha=0.5) of its current value and the values."""
    current_ema = mapping.get(key)

    for value in values:
        current_ema = value if current_ema is None else (value + current_ema) * 0.5

    mapping[key] = current_ema


class Aggregation(Enum):
    @dataclass(frozen=True)
    class Item:
        collection_type: type | None
        func: Callable[[MutableMapping, Any, Iterable[Any]], None]

    """
    Define an enumeration class for data aggregation modes.
    All aggregators now accept an iterable of values.
    """
    ALL = Item(collection_type=list, func=all_aggregator)
    """Aggregate all values into a list."""
    COUNT = Item(collection_type=Counter, func=count_aggregator)
    """Count occurrences of each value."""
    DISTINCT = Item(collection_type=set, func=distinct_aggregator)
    """Aggregate distinct values into a set."""
    FIRST = Item(collection_type=None, func=first_aggregator)
    """Take the first value encountered."""
    LAST = Item(collection_type=None, func=last_aggregator)
    """Take the last value encountered."""
    SUM = Item(collection_type=float, func=sum_aggregator)
    """Sum all values."""
    MAX = Item(collection_type=float, func=max_aggregator)
    """Take the maximum value."""
    MIN = Item(collection_type=float, func=min_aggregator)
    """Take the minimum value."""
    EMA = Item(collection_type=float, func=ema_aggregator)
    """Calculate the exponential moving average of values."""

    @property
    def collection_type(self) -> type | None:
        """
        Return the collection type used for this aggregation mode.
        """
        return self.value.collection_type

    @property
    def aggregator(self) -> Callable[[MutableMapping, Any, Iterable[Any]], None]:
        """
        Return the aggregator function for this mode.
        """
        return self.value.func
