from collections import defaultdict
from collections.abc import Callable, Generator, Iterable, Mapping
from itertools import chain
from typing import Any

try:
    from warnings import deprecated
except ImportError:
    from deprecated import deprecated

from mappingtools._tools import _is_strict_iterable
from mappingtools.aggregation import Aggregation
from mappingtools.collectors.mapping_collector import MappingCollector
from mappingtools.typing import K

__all__ = [
    "distinct",
    "flatten",
    "inverse",
    "keep",
    "pivot",
    "rekey",
    "remove",
    "rename",
    "stream",
    "stream_dict_records",
]


@deprecated("Can be easily replaced with a Python comprehension expression. See DocString for more info.")
def _take(keys: Iterable[K], mapping: Mapping[K, Any], exclude: bool = False) -> dict[K, Any]:
    """
    .. deprecated:: 0.8.0
       Use a dictionary comprehension instead.
       Will be removed in version 0.9.0

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


@deprecated("Can be easily replaced with a Python comprehension expression. See DocString for more info.")
def keep(keys: Iterable[K], *mappings: Mapping[K, Any]) -> Generator[Mapping[K, Any], Any, None]:
    """
    .. deprecated:: 0.8.0
       Use a generator expression with a dictionary comprehension instead.
       Example: `({k: m[k] for k in keys if k in m} for m in mappings)`
       Will be removed in version 0.9.0

    Yield a subset of mappings by keeping only the specified keys.

    Args:
        keys (Iterable[K]): The keys to keep in the mappings.
        *mappings (Mapping[K, Any]): Variable number of mappings to filter.

    Yields:
        Generator[Mapping[K, Any], Any, None]: A generator of mappings with only the specified keys.
    """
    yield from (_take(keys, mapping) for mapping in mappings)


@deprecated("Can be easily replaced with a Python comprehension expression. See DocString for more info.")
def remove(keys: Iterable[K], *mappings: Mapping[K, Any]) -> Generator[Mapping[K, Any], Any, None]:
    """
    .. deprecated:: 0.8.0
       Use a generator expression with a dictionary comprehension instead.
       Example: `({k: v for k, v in m.items() if k not in keys} for m in mappings)`
       Will be removed in version 0.9.0

    Yield a subset of mappings by removing the specified keys.

    Args:
        keys (Iterable[K]): The keys to remove from the mappings.
        *mappings (Mapping[K, Any]): Variable number of mappings to filter.

    Yields:
        Generator[Mapping[K, Any], Any, None]: A generator of mappings with specified keys removed.
    """
    yield from (_take(keys, mapping, exclude=True) for mapping in mappings)


@deprecated("Can be easily replaced with a Python comprehension expression. See DocString for more info.")
def stream(mapping: Mapping, item_factory: Callable[[Any, Any], Any] | None = None) -> Generator[Any, Any, None]:
    """
    .. deprecated:: 0.8.0
       Use `mapping.items()` or a generator comprehension instead.
       Example: `(item_factory(k, v) for k, v in mapping.items())`
       Will be removed in version 0.9.0

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


@deprecated("Can be easily replaced with a Python comprehension expression. See DocString for more info.")
def stream_dict_records(
    mapping: Mapping, key_name: str = "key", value_name: str = "value"
) -> Generator[Mapping[str, Any], Any, None]:
    """
    .. deprecated:: 0.8.0
       Use a generator expression with a dictionary literal instead.
       Example: `({key_name: k, value_name: v} for k, v in mapping.items())`
       Will be removed in version 0.9.0

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


def flatten(mapping: Mapping[Any, Any], delimiter: str | None = None) -> dict[tuple | str, Any]:
    """
    Flatten a nested mapping structure into a single-level dictionary.

    Args:
        mapping (Mapping[Any, Any]): The nested mapping to flatten.
        delimiter (str | None): Uses this delimiter to join the path parts. If None then return path tuple.

    Returns:
        dict
    """

    def _flatten(key: tuple, value: Any):
        if isinstance(value, Mapping):
            for k, v in value.items():
                new_key = tuple([*key, *k] if _is_strict_iterable(k) else [*key, k])
                yield from _flatten(new_key, v)
        else:
            yield key, value

    flattened = _flatten((), mapping)

    if delimiter is not None:
        flattened = ((delimiter.join(map(str, k)), v) for k, v in flattened)

    return dict(flattened)


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


def pivot(
    iterable: Iterable[Mapping],
    *,
    index: str,
    columns: str,
    values: str,
    mode: Aggregation = Aggregation.LAST,
) -> dict[Any, dict[Any, Any]]:
    """
    Reshape data (produce a "pivot" table) based on column values.

    Args:
        iterable: An iterable of mappings (e.g., list of dicts).
        index: The key to use for the row labels.
        columns: The key to use for the column labels.
        values: The key to use for the values.
        mode: The aggregation mode to use for values. Defaults to Aggregation.LAST.

    Returns:
        A nested dictionary: {index_value: {column_value: aggregated_value}}.
    """
    # Initialize inner collectors based on mode
    # We use a functional primitive to determine the collection type
    ctype = mode.collection_type
    result = (
        defaultdict(lambda: defaultdict(ctype))
        if ctype
        else defaultdict(dict)
    )

    # Optimization: Bind a specialized aggregator function to the local scope
    aggregate = mode.aggregator

    for item in iterable:
        # Skip items that don't have the required keys
        if index not in item or columns not in item or values not in item:
            continue

        row_key = item[index]
        col_key = item[columns]
        val = item[values]

        aggregate(result[row_key], col_key, val)

    # Convert defaultdicts to regular dicts for clean output
    # This is a deep conversion
    final_result = {}
    for row_k, row_v in result.items():
        final_result[row_k] = dict(row_v)

    return final_result


def rename(
    mapping: Mapping[K, Any],
    mapper: Mapping[K, K] | Callable[[K], K],
    *,
    aggregation: Aggregation = Aggregation.LAST,
) -> dict[K, Any]:
    """
    Rename keys in a mapping based on a mapper (Mapping or Callable).

    This operator creates a new dictionary with renamed keys. If a key is not
    present in the mapper, it remains unchanged. Collisions (when multiple
    original keys map to the same new key) are handled according to the
    specified aggregation.

    Args:
        mapping: The source mapping.
        mapper: A dictionary mapping old keys to new keys, or a function that transforms keys.
        aggregation: How to handle key collisions. Defaults to Aggregation.LAST.

    Returns:
        A new dictionary with renamed keys and aggregated values.
    """

    def key_factory(k: K, _: Any) -> K:
        if isinstance(mapper, Mapping):
            return mapper.get(k, k)
        return mapper(k)

    return rekey(mapping, key_factory, aggregation=aggregation)


def rekey(
    mapping: Mapping[Any, Any],
    key_factory: Callable[[Any, Any], K],
    *,
    aggregation: Aggregation = Aggregation.LAST,
) -> dict[K, Any]:
    """
    Transform keys of a mapping based on a factory function of (key, value).

    This allows "re-indexing" a mapping where the new key depends on the content
    of the value or a combination of the old key and value. Collisions are
    handled according to the specified aggregation.

    Args:
        mapping: The source mapping.
        key_factory: A callable that takes (key, value) and returns the new key.
        aggregation: How to handle key collisions. Defaults to Aggregation.LAST.

    Returns:
        A new dictionary with keys generated by the factory and aggregated values.
    """
    collector = MappingCollector(aggregation=aggregation)
    # Optimization: Bind the aggregator to a local variable
    aggregate = aggregation.aggregator
    target = collector._mapping

    for k, v in mapping.items():
        aggregate(target, key_factory(k, v), v)

    return collector.mapping
