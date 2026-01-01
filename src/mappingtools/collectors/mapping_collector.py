from collections import defaultdict
from collections.abc import Iterable, Mapping, MutableMapping
from typing import Generic

from mappingtools.aggregation import Aggregation
from mappingtools.typing import KT, VT, VT_co

# Alias for backward compatibility
MappingCollectorMode = Aggregation


class MappingCollector(Generic[KT, VT_co]):
    def __init__(self, aggregation: Aggregation = Aggregation.ALL, **kwargs):
        """
        Initialize the MappingCollector with the specified mode.

        Args:
            aggregation (Aggregation): The mode for collecting mappings.
            *args: Variable positional arguments used to initialize the internal mapping.
            **kwargs: Variable keyword arguments used to initialize the internal mapping.
        """
        self._mapping: MutableMapping[KT, VT_co]

        if not isinstance(aggregation, Aggregation):
            raise TypeError(f"Invalid mode type: {type(aggregation)}. Expected Aggregation.")

        self.aggregation = aggregation
        self._aggregator = self.aggregation.aggregator
        aggregation_collection_type = self.aggregation.collection_type

        if aggregation_collection_type:
            self._mapping = defaultdict(aggregation_collection_type, **kwargs)
        else:
            self._mapping = dict(**kwargs)

    def __repr__(self):
        return f"MappingCollector(aggregation={self.aggregation}, mapping={self.mapping})"

    @property
    def mapping(self) -> dict[KT, VT_co]:
        """
        Return a shallow copy of the internal mapping.

        Returns:
            dict[KT, VT_co]: A shallow copy of the internal mapping.
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
        self._aggregator(self._mapping, key, value)

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
