import itertools
from collections import defaultdict
from collections.abc import Callable, Generator, Iterable, Mapping, Sequence
from copy import deepcopy
from enum import Enum, member
from itertools import chain
from typing import Any, overload

from mappingtools.aggregations import Aggregation
from mappingtools.resolvers import DecisionMetric, LogicalResolver, NumericResolver, Resolver, ResolverType
from mappingtools.traversal import _is_traversal_iterable
from mappingtools.typing import MISSING, Combine, K, Missing, T, Tree

__all__ = [
    'KeyFormat',
    'combine',
    'distinct',
    'flatten',
    'inverse',
    'merge',
    'pivot',
    'rekey',
    'rename',
    'reshape',
]

# region combine

def _combine(  # noqa: C901
        t1: Any,
        t2: Any,
        op: Any,
        metric_ops: dict[str, Any] | None = None,
        collect: bool = False,
) -> Any:
    def metric_results(t: Any, side: int) -> dict[str, Any]:
        return {k: DecisionMetric.calculate(t, side, v) for k, v in metric_ops.items()}

    def nullified_result(t: Any) -> dict[str, Any]:
        none_tree = DecisionMetric.nullify(t)
        return {k: deepcopy(none_tree) for k in metric_ops}

    # 1) If one side is MISSING, the other wins unconditionally.
    if t1 is MISSING:
        return (t2, metric_results(t2, 1)) if collect else t2
    if t2 is MISSING:
        return (t1, metric_results(t1, 0)) if collect else t1

    # 2) If both are dicts, recursively combine.
    if isinstance(t1, dict) and isinstance(t2, dict):
        combined = {}
        metrics = {name: {} for name in metric_ops} if collect else None
        all_keys = set(t1.keys()) | set(t2.keys())
        for k in all_keys:
            res = _combine(t1.get(k, MISSING), t2.get(k, MISSING), op, metric_ops, collect)
            val = res[0] if collect else res
            if val is not MISSING:
                combined[k] = val
                if collect:
                    m_dict = res[1]
                    for metric_name in metric_ops:
                        metrics[metric_name][k] = m_dict[metric_name]
        return (combined, metrics) if collect else combined

    # 3) If both are lists, recursively combine by position.
    if isinstance(t1, list) and isinstance(t2, list):
        combined = []
        metrics = {name: [] for name in metric_ops} if collect else None
        zipped = itertools.zip_longest(t1, t2, fillvalue=MISSING)
        for i1, i2 in zipped:
            res = _combine(i1, i2, op, metric_ops, collect)
            val = res[0] if collect else res
            combined.append(val)
            if collect:
                m_dict = res[1]
                for metric_name in metric_ops:
                    metrics[metric_name].append(m_dict[metric_name])
        return (combined, metrics) if collect else combined

    # 4) Otherwise, there is a conflict. Resolve it.
    resolved = op(t1, t2)
    if resolved is MISSING:
        return (MISSING, dict.fromkeys(metric_ops, MISSING)) if collect else MISSING

    # Check resolved container shape to prevent shape divergence
    if isinstance(resolved, (dict, list)):
        if collect:
            if resolved is t1 or resolved == t1:
                return resolved, metric_results(resolved, 0)
            elif resolved is t2 or resolved == t2:
                return resolved, metric_results(resolved, 1)
            else:
                return resolved, nullified_result(resolved)
        else:
            return resolved

    if collect:
        res_metrics = {}
        for metric_name, metric_op in metric_ops.items():
            res_metrics[metric_name] = metric_op(t1, t2, resolved)
        return resolved, res_metrics

    return resolved



@overload
def combine(
        tree1: Tree[T] | Missing = MISSING,
        tree2: Tree[T] | Missing = MISSING,
        op: Combine | ResolverType = Resolver.LAST,
        decision_metrics: None = None,
) -> Tree[T] | Any:
    ...


@overload
def combine(
        tree1: Tree[T] | Missing = MISSING,
        tree2: Tree[T] | Missing = MISSING,
        op: Combine | ResolverType = Resolver.LAST,
        decision_metrics: list[DecisionMetric | Callable[[Any, Any, Any], Any]] = ...,
) -> tuple[Tree[T] | Any, dict[str, Tree[Any] | Any]]:
    ...


def combine(
        tree1: Tree[T] | Missing = MISSING,
        tree2: Tree[T] | Missing = MISSING,
        op: Combine | ResolverType = Resolver.LAST,
        decision_metrics: list[DecisionMetric | Callable[[Any, Any, Any], Any]] | None = None,
) -> Any:
    """
    Combines two trees using a binary operator `op` that resolves conflicts at the leaf nodes.
    Optionally extracts decision metrics of the combination process in a single recursive pass.

    Args:
        tree1: The first tree structure.
        tree2: The second tree structure.
        op: A resolver strategy or custom callable to handle conflicts. Defaults to Resolver.LAST.
        decision_metrics: An optional list of DecisionMetric enums or custom callable metrics.

    Returns:
        The combined tree structure if decision_metrics is None, otherwise a 2-tuple containing:
        1. The combined tree structure.
        2. A dictionary mapping each metric's name to its corresponding metric tree.
    """
    if isinstance(op, (Resolver, LogicalResolver, NumericResolver)):
        op = op.value

    metric_ops = {}
    if decision_metrics is not None and isinstance(decision_metrics, list):
        metric_ops = dict(
            (v.name, v.value) if isinstance(v, DecisionMetric) else (getattr(v, "__name__", str(v)), v)
            for v in decision_metrics
        )

    collect = decision_metrics is not None
    return _combine(tree1, tree2, op, metric_ops, collect=collect)

# endregion combine

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


def _flatten_step_tuple(path: tuple, part: Any) -> tuple:
    return *path, part


def _flatten_step_str(path: str, part: Any) -> str:
    formatted_part = f'"{part}"' if isinstance(part, str) else str(part)
    return f"{path},{formatted_part}" if path else formatted_part


def _flatten_step_pointer(path: str, part: Any) -> str:
    formatted_part = str(part).replace("~", "~0").replace("/", "~1") if isinstance(part, str) else str(part)
    return f"{path}/{formatted_part}"


def _flatten_step_jsonpath(path: str, part: Any) -> str:
    if (isinstance(part, str)
            and part
            and part.replace('_', '').isalnum()
            and not part.isdigit()
            and not part[0].isdigit()
    ):
        return f"{path}.{part}"
    elif isinstance(part, int):
        return f"{path}[{part}]"
    else:
        return f'{path}["{part}"]'


def _flatten_step_javascript(path: str, part: Any) -> str:
    if (isinstance(part, str)
            and part
            and part.replace('_', '').isalnum()
            and not part.isdigit()
            and not part[0].isdigit()
    ):
        return f"{path}.{part}" if path else part
    elif isinstance(part, int):
        return f"{path}[{part}]" if path else f"[{part}]"
    else:
        return f'{path}["{part}"]' if path else f'["{part}"]'


class KeyFormat(Enum):
    TUPLE = member(((), _flatten_step_tuple))
    STR = member(('', _flatten_step_str))
    JAVASCRIPT = member(('', _flatten_step_javascript))
    JSONPATH = member(('$', _flatten_step_jsonpath))
    JSONPOINTER = member(('', _flatten_step_pointer))


def flatten(data: Tree[Any], key_format: KeyFormat = KeyFormat.TUPLE) -> Tree[Any]:
    """
    Flatten a nested tree structure (dicts and lists) into a single-level dictionary.

    Args:
        data (Tree[Any]): The nested mapping or list to flatten.
        key_format (KeyFormat): The format for keys. Defaults to KeyFormat.TUPLE.

    Returns:
        Tree[Any]: The flattened dictionary.
    """
    result = {}
    initial, step = key_format.value

    def _recurse(value: Any, current_path: Any):
        if isinstance(value, dict):
            for k, v in value.items():
                # Fast path for common atomic keys (str, int)
                if isinstance(k, (str, int)):  # NOSONAR
                    _recurse(v, step(current_path, k))
                elif _is_traversal_iterable(k):
                    # k is a tuple/list/iterable, extend path
                    # We need to convert to tuple first to know length or iterate safely if it's a generator.
                    k_seq = tuple(k)
                    next_path = current_path
                    for part in k_seq:
                        next_path = step(next_path, part)
                    _recurse(v, next_path)
                else:
                    _recurse(v, step(current_path, k))
        elif isinstance(value, list):
            for i, v in enumerate(value):
                _recurse(v, step(current_path, i))
        else:
            result[current_path] = value

    _recurse(data, initial)
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


def merge(tree1: Tree[T] | Missing = MISSING, tree2: Tree[T] | Missing = MISSING) -> Tree[T]:
    """
    A pure function (Monoid operation) to deeply merge two recursive tree structures.
    The merging strategy resolves conflicts by overwriting existing values with new ones (right-side precedence).
    `MISSING` acts as the identity element.

    Mathematically, this operation forms a composite Monoid:
    - Last Monoid (Scalar Fallback): When resolving conflicts between simple values, the right-hand
      side (`tree2`) wins.
    - Pointwise Monoid (Dictionary Merge): If the values are dictionaries, they are merged by key,
      recursively calling `merge` on the values.
    - Zip Monoid (List Merge): If both are lists, they are zipped and merged positionally,
      substituting `MISSING` for missing indices.
    - Free Monoid (Mixed List/Scalar): If one is a list and the other is a scalar/dict,
      it concatenates (appends/prepends).

    Because it forms a Monoid, this function can be used with `functools.reduce` to collect
    an iterable of trees into a single structure.

    Args:
        tree1 (Tree[T] | Missing): The first tree structure.
        tree2 (Tree[T] | Missing): The second tree structure.

    Returns:
        Tree[T] | Missing: The deeply merged tree structure.
    """
    if isinstance(tree1, dict) and isinstance(tree2, dict):
        merged = dict(tree1)
        for k, v in tree2.items():
            merged[k] = merge(merged.get(k, MISSING), v)
        return merged
    elif isinstance(tree1, list) and isinstance(tree2, list):
        # zip longest to handle different lengths, filling missing values with MISSING
        zipped = itertools.zip_longest(tree1, tree2, fillvalue=MISSING)
        return [merge(t1, t2) for t1, t2 in zipped]
    elif isinstance(tree1, list) and not isinstance(tree2, list) and tree2 is not MISSING:
        # If tree1 is a list and tree2 is not, append tree2 to a new list
        return [*tree1, tree2]
    elif not isinstance(tree1, list) and tree1 is not MISSING and isinstance(tree2, list):
        # If tree2 is a list and tree1 is not, prepend tree1 to a new list
        return [tree1, *tree2]
    elif tree1 is MISSING:
        return tree2
    elif tree2 is MISSING:
        return tree1
    else:
        # If both are values (not dicts or lists), or one is a value and the other is a dict/list,
        # the non-MISSING value takes precedence.
        # If both are non-MISSING and different types, tree2 overwrites tree1.
        return tree2


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

        # Pass value as a tuple because aggregator expects iterable
        aggregate(result[row_key], col_key, (val,))

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
        # Pass value as a tuple because aggregator expects iterable
        aggregate(target, key_factory(k, v), (v,))

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
            current[leaf_val] = ctype()

        # Pass value as a tuple because aggregator expects iterable
        aggregate(current, leaf_val, (value_val,))

    return result
