from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Mapping
from enum import Enum, auto
from typing import Any

from mappingtools.typing import KT, VT, Category, VT_co


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
    Define an enumeration class for mapping collector modes.

    Attributes:
        ALL: Collect all values for each key.
        COUNT: Count the occurrences of each value for each key.
        DISTINCT: Collect distinct values for each key.
        FIRST: Collect the first value for each key.
        LAST: Collect the last value for each key.


    """
    ALL = auto()
    COUNT = auto()
    DISTINCT = auto()
    FIRST = auto()
    LAST = auto()


class MappingCollector:

    def __init__(self, mode: MappingCollectorMode = MappingCollectorMode.ALL, **kwargs):
        """
        Initialize the MappingCollector with the specified mode.

        Args:
            mode (MappingCollectorMode): The mode for collecting mappings.
            *args: Variable positional arguments used to initialize the internal mapping.
            **kwargs: Variable keyword arguments used to initialize the internal mapping.
        """
        self._mapping: Mapping[KT, VT_co]

        self.mode = mode

        match self.mode:
            case MappingCollectorMode.ALL:
                self._mapping = defaultdict(list, **kwargs)
            case MappingCollectorMode.COUNT:
                self._mapping = defaultdict(Counter, **kwargs)
            case MappingCollectorMode.DISTINCT:
                self._mapping = defaultdict(set, **kwargs)
            case MappingCollectorMode.FIRST | MappingCollectorMode.LAST:
                self._mapping = dict(**kwargs)
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
