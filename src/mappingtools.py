import dataclasses
import inspect
from collections import defaultdict
from collections.abc import Callable, Generator, Iterable, Mapping
from itertools import chain
from typing import Any, TypeVar

K = TypeVar("K")


def _take(keys: Iterable[K], mapping: Mapping[K, Any], exclude: bool = False) -> dict[K, Any]:
    if not isinstance(mapping, Mapping):
        raise TypeError(f"Parameter 'mapping' should be of type 'Mapping', but instead is type '{type(mapping)}'")

    mapping_keys = set(mapping.keys())
    keys = set(keys) & mapping_keys  # intersection with keys to get actual existing keys
    if exclude:
        keys = mapping_keys - keys

    return {k: mapping.get(k) for k in keys}


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
        value = mapping.get(key, )
        value_type_pair = (value, type(value))
        if key in mapping and value_type_pair not in distinct_value_type_pairs:
            distinct_value_type_pairs.add(value_type_pair)
            yield value


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


def inverse(mapping: Mapping[Any, set]) -> Mapping[Any, set]:
    """Return a new dictionary with keys and values swapped from the input mapping.

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


def _is_strict_iterable(obj: Iterable) -> bool:
    return isinstance(obj, Iterable) and not isinstance(obj, str | bytes | bytearray)


def _is_class_instance(obj) -> bool:
    return (dataclasses.is_dataclass(obj) and not isinstance(obj, type)) or hasattr(obj, '__dict__')


def _process_obj(obj: Any,
                 mapping_handler: Callable | None = None,
                 iterable_handler: Callable | None = None,
                 class_handler: Callable | None = None,
                 *args,
                 **kwargs):
    if callable(mapping_handler) and isinstance(obj, Mapping):
        return mapping_handler(obj, *args, **kwargs)
    elif callable(iterable_handler) and _is_strict_iterable(obj):
        return iterable_handler(obj, *args, **kwargs)
    elif callable(class_handler) and _is_class_instance(obj):
        return class_handler(obj, *args, **kwargs)
    else:
        return obj


def dictify(obj, key_converter: Callable[[Any], str] | None = None):
    """Dictify an object using a specified key converter.

    Args:
        obj (Any): The object to be dictified.
        key_converter (Optional[Callable[[Any], str]], optional): A function to convert keys. Defaults to None.

    Returns:
        The dictified object.
    """
    return _process_obj(obj, _dictify_mapping, _dictify_iterable, _dictify_class, key_converter=key_converter)


def _dictify_mapping(obj, key_converter: Callable[[Any], str] | None = None) -> dict:
    return {(key_converter(k) if key_converter else k): dictify(v, key_converter) for k, v in obj.items()}


def _dictify_iterable(obj, key_converter: Callable[[Any], str] | None = None) -> list:
    return [dictify(v, key_converter) for v in obj]


def _dictify_class(obj, key_converter: Callable[[Any], str] | None = None) -> dict | str:
    return {
        (key_converter(k) if key_converter else k): dictify(v, key_converter)
        for k, v in inspect.getmembers(obj)
        if not k.startswith('_')
    }


def nested_defaultdict(nesting_depth: int = 0, default_factory: Callable | None = None, **kwargs) -> defaultdict:
    """Return a nested defaultdict with the specified nesting depth and default factory.
    A nested_defaultdict with nesting_depth=0 is equivalent to builtin 'collections.defaultdict'.
    Each nesting_depth increment effectively adds an additional item accessor.

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


def unwrap(obj: Any):
    """
    Unwraps the given object.

    Args:
        obj (Any): The object to unwrap.

    Returns:
        Any: The unwrapped object.
    """
    return _process_obj(obj, _unwrap_mapping, _unwrap_iterable, _unwrap_class)


def _unwrap_mapping(obj: Mapping) -> list[dict]:
    return [{'key': k, 'value': unwrap(v)} for k, v in obj.items()]


def _unwrap_iterable(obj: Iterable) -> list:
    return [unwrap(v) for v in obj]


def _unwrap_class(obj):
    return [{'key': k, 'value': unwrap(v)} for k, v in inspect.getmembers(obj) if not k.startswith('_')]


__all__ = ('dictify', 'distinct', 'keep', 'inverse', 'nested_defaultdict', 'remove', 'unwrap')
