import dataclasses
import inspect
from collections import Counter, defaultdict
from collections.abc import Callable, Generator, Iterable, Mapping
from enum import Enum, auto
from itertools import chain
from typing import Any, TypeVar

K = TypeVar('K')
KT = TypeVar('KT')
VT = TypeVar('VT')
VT_co = TypeVar('VT_co')

Category = TypeVar('Category', bound=str | tuple | int | float)


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


class MappingCollectorMode(Enum):
    """
    Define an enumeration class for mapping collector modes with two options: one_to_one and one_to_many.
    """
    ALL = auto()
    COUNT = auto()
    DISTINCT = auto()
    FIRST = auto()
    LAST = auto()


class MappingCollector:

    def __init__(self, mode: MappingCollectorMode = MappingCollectorMode.ALL, *args, **kwargs):
        """
        Initialize the MappingCollector with the specified mode.

        Args:
            mode (MappingCollectorMode): The mode for collecting mappings.
            *args: Variable positional arguments used to initialize the internal mapping.
            **kwargs: Variable keyword arguments used to initialize the internal mapping.
        """

        self.mode = mode

        match self.mode:
            case MappingCollectorMode.ALL:
                self._mapping = defaultdict(list, *args, **kwargs)
            case MappingCollectorMode.COUNT:
                self._mapping = defaultdict(Counter, *args, **kwargs)
            case MappingCollectorMode.DISTINCT:
                self._mapping = defaultdict(set, *args, **kwargs)
            case MappingCollectorMode.FIRST | MappingCollectorMode.LAST:
                self._mapping = dict(*args, **kwargs)
            case _:
                raise ValueError("Invalid mode")

    def __repr__(self):
        return f'MappingCollector(mode={self.mode}, mapping={self.mapping})'

    @property
    def mapping(self) -> Mapping[KT, VT_co]:
        """
        Return a shallow copy of the internal mapping.

        Returns:
            Mapping[KT, VT_co]: A shallow copy of the internal mapping.
        """
        return dict(self._mapping)

    def add(self, key: KT, value: VT):
        """
        Add a key-value pair to the internal mapping based on the specified mode.

        Args:
            key: The key to be added to the mapping.
            value: The value corresponding to the key.

        Returns:
            None
        """
        match self.mode:
            case MappingCollectorMode.ALL:
                self._mapping[key].append(value)
            case MappingCollectorMode.COUNT:
                self._mapping[key].update({value: 1})
            case MappingCollectorMode.DISTINCT:
                self._mapping[key].add(value)
            case MappingCollectorMode.FIRST if key not in self.mapping:
                self._mapping[key] = value
            case MappingCollectorMode.LAST:
                self._mapping[key] = value

    def collect(self, iterable: Iterable[tuple[KT, VT]]):
        """
        Collect key-value pairs from the given iterable and add them to the internal mapping
        based on the specified mode.

        Args:
            iterable (Iterable[tuple[KT, VT]]): An iterable containing key-value pairs to collect.

        Returns:
            None
        """
        for k, v in iterable:
            self.add(k, v)


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


def _is_strict_iterable(obj: Iterable) -> bool:
    return isinstance(obj, Iterable) and not isinstance(obj, str | bytes | bytearray)


def _is_class_instance(obj) -> bool:
    return (dataclasses.is_dataclass(obj) and not isinstance(obj, type)) or hasattr(obj, '__dict__')


def _class_generator(obj):
    yield from ((k, v) for k, v in inspect.getmembers(obj) if not k.startswith('_'))


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


def _strictify_mapping(obj, key_converter, value_converter):
    return {
        (key_converter(k) if key_converter else k): strictify(value_converter(v) if value_converter else v,
                                                              key_converter=key_converter,
                                                              value_converter=value_converter)
        for k, v in obj.items()}


def _strictify_iterable(obj, key_converter, value_converter):
    return [strictify(value_converter(v) if value_converter else v,
                      key_converter=key_converter,
                      value_converter=value_converter)
            for v in obj]


def _strictify_class(obj, key_converter, value_converter):
    return {
        (key_converter(k) if key_converter else k): strictify(value_converter(v) if value_converter else v,
                                                              key_converter=key_converter,
                                                              value_converter=value_converter)
        for k, v in _class_generator(obj)
    }


def strictify(obj: any,
              key_converter: Callable[[Any], str] | None = None,
              value_converter: Callable[[Any], Any] | None = None) -> Any:
    """Applies strict structural conversion to the given object using optional specific converters for keys and values.

       Args:
           obj: The object to be converted.
           key_converter: A function to convert keys (optional).
           value_converter: A function to convert values (optional).

       Returns:
           The object content after applying the conversion.
       """
    return _process_obj(obj, _strictify_mapping, _strictify_iterable, _strictify_class,
                        key_converter=key_converter,
                        value_converter=value_converter)


def simplify(obj: Any) -> Any:
    """Dictify recursively the given object.

    Args:
        obj (Any): The object to be simplified.

    Returns:
        The simplified object.
    """
    return strictify(obj, key_converter=str)


def listify(obj: Any, key_name: str = 'key', value_name: str = 'value') -> Any:
    """
    listify recursively the given object.

    Args:
        obj (Any): The object to unwrap.
        key_name(str): The key field name.
        value_name(str): The value field name.

    Returns:
        Any: The unwrapped object.

    """
    return _process_obj(obj, _listify_mapping, _listify_iterable, _listify_class,
                        key_name=key_name, value_name=value_name)


def _listify_mapping(obj: Mapping, key_name, value_name) -> list[dict]:
    return [{key_name: k, value_name: listify(v, key_name, value_name)} for k, v in obj.items()]


def _listify_iterable(obj: Iterable, key_name, value_name) -> list:
    return [listify(v, key_name, value_name) for v in obj]


def _listify_class(obj, key_name, value_name):
    return [{key_name: k, value_name: listify(v, key_name, value_name)} for k, v in inspect.getmembers(obj) if
            not k.startswith('_')]


__all__ = (
    'distinct', 'keep', 'remove', 'inverse', 'nested_defaultdict', 'listify', 'simplify', 'strictify', 'Category',
    'CategoryCounter', 'MappingCollector', 'MappingCollectorMode'
)
