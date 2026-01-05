from collections import defaultdict
from collections.abc import Callable, Generator, Iterable, Mapping, Sequence
from itertools import chain
from typing import Any

from mappingtools._tools import _is_strict_iterable
from mappingtools.aggregation import Aggregation
from mappingtools.typing import K

__all__ = [
    'distinct',
    'flatten',
    'inverse',
    'pivot',
    'rekey',
    'rename',
    'reshape',
]


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
    result = {}
    path = []

    def _recurse(value: Any):
        if isinstance(value, Mapping):
            for k, v in value.items():
                # Fast path for common atomic keys (str, int)
                if isinstance(k, (str, int)):
                    path.append(k)
                    _recurse(v)
                    path.pop()
                elif _is_strict_iterable(k):
                    # k is a tuple/list/iterable, extend path
                    # We need to convert to list to know length for backtracking if it's a generator
                    # But _is_strict_iterable allows generators.
                    # If k is a generator, extending path consumes it.
                    # We can't easily know how many items were added without counting.
                    # So we convert to tuple/list first.
                    k_seq = tuple(k)
                    path.extend(k_seq)
                    _recurse(v)
                    # Backtrack
                    del path[-len(k_seq) :]
                else:
                    path.append(k)
                    _recurse(v)
                    path.pop()
        else:
            result[tuple(path)] = value

    _recurse(mapping)

    if delimiter is not None:
        return {delimiter.join(map(str, k)): v for k, v in result.items()}

    return result


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

    return dict(dd)


def pivot(
    iterable: Iterable[Mapping],
    *,
    index: str,
    columns: str,
    values: str,
    aggregation: Aggregation = Aggregation.LAST,
) -> dict[Any, dict[Any, Any]]:
    """
    Reshape data (produce a "pivot" table) based on column values.

    Args:
        iterable: An iterable of mappings (e.g., list of dicts).
        index: The key to use for the row labels.
        columns: The key to use for the column labels.
        values: The key to use for the values.
        aggregation: The aggregation mode to use for values. Defaults to Aggregation.LAST.

    Returns:
        A nested dictionary: {index_value: {column_value: aggregated_value}}.
    """
    # Initialize inner collectors based on mode
    # We use a functional primitive to determine the collection type
    ctype = aggregation.collection_type
    result = defaultdict(lambda: defaultdict(ctype)) if ctype else defaultdict(dict)

    # Optimization: Bind a specialized aggregator function to the local scope
    aggregate = aggregation.aggregator

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
    ctype = aggregation.collection_type
    target = defaultdict(ctype) if ctype else {}

    aggregate = aggregation.aggregator

    for k, v in mapping.items():
        aggregate(target, key_factory(k, v), v)

    return dict(target)


def reshape(
    iterable: Iterable[Mapping],
    keys: Sequence[str | Callable[[Mapping], Any]],
    value: str | Callable[[Mapping], Any],
    aggregation: Aggregation = Aggregation.LAST,
) -> dict[Any, Any]:
    """
    Reshape a stream of mappings into a nested dictionary (tensor) of arbitrary depth.

    This is a generalization of `pivot` that supports N-dimensional nesting.

    Args:
        iterable: An iterable of mappings (records).
        keys: A sequence of keys (or callables) to use for the nesting hierarchy.
        value: The key (or callable) to use for the leaf values.
        aggregation: The aggregation mode to use for collisions at the leaf.

    Returns:
        A nested dictionary where the depth equals len(keys).
    """
    if not keys:
        return {}

    # The root of our tensor
    result = {}

    # Optimization: Bind the aggregator
    aggregate = aggregation.aggregator
    ctype = aggregation.collection_type

    # Optimization: Pre-calculate slice indices
    path_keys = keys[:-1]
    leaf_key = keys[-1]

    for item in iterable:
        # Navigate/Build the tree structure
        current = result
        for k in path_keys:
            key_val = k(item) if callable(k) else item.get(k)

            if key_val not in current:
                current[key_val] = {}

            current = current[key_val]

        leaf_val = leaf_key(item) if callable(leaf_key) else item.get(leaf_key)
        value_val = value(item) if callable(value) else item.get(value)

        # Apply aggregation at the leaf
        if ctype and leaf_val not in current:
            current[item.get(leaf_key)] = ctype()

        aggregate(current, leaf_val, value_val)

    return result
