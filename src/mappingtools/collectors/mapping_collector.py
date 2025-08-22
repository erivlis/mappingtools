from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from enum import Enum, auto

from mappingtools.typing import KT, VT, VT_co


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
