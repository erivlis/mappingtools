from collections import defaultdict
from collections.abc import Callable, Iterable, MutableMapping
from typing import Any, Generic, cast

from mappingtools.aggregation import Aggregation
from mappingtools.typing import KT, VT, Category, VT_co

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
            raise TypeError(f'Invalid mode type: {type(aggregation)}. Expected Aggregation.')

        self.aggregation = aggregation
        self._aggregator = self.aggregation.aggregator
        aggregation_collection_type = self.aggregation.collection_type

        if aggregation_collection_type:
            self._mapping = defaultdict(aggregation_collection_type, **kwargs)
        else:
            self._mapping = dict(**kwargs)

    def __repr__(self):
        return f'MappingCollector(aggregation={self.aggregation}, mapping={self.mapping})'

    @property
    def mapping(self) -> dict[KT, VT_co]:
        """
        Return a shallow copy of the internal mapping.

        Returns:
            dict[KT, VT_co]: A shallow copy of the internal mapping.
        """
        return dict(self._mapping)

    def add(self, key: KT, *values: VT):
        """
        Add one or more values to the internal mapping based on the specified mode.

        Args:
            key: The key to be added to the mapping.
            *values: The values corresponding to the key.

        Returns:
            None
        """
        if values:
            self._aggregator(self._mapping, key, values)

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


class CategoryCollector(defaultdict[str, MappingCollector[Category, VT_co]]):
    def __init__(self, aggregation: Aggregation = Aggregation.ALL, **kwargs: Any):
        """
        Initialize the CategoryCollector with the specified aggregation mode.

        Args:
            aggregation (Aggregation): The mode for collecting mappings.
        """
        self.aggregation = aggregation
        super().__init__(lambda: MappingCollector(aggregation=aggregation, **kwargs))

    def __repr__(self):
        return f'CategoryCollector(aggregation={self.aggregation}, mapping={dict(self)})'

    def add(self, data: VT_co, **categories: Category | Callable[[VT_co], Category]):
        """
        Add a single value to the appropriate category in the collector.

        Args:
            data: The value to be added to the mapping.
            **categories: Keyword arguments where keys are category names and values are either
                          category values or callables that return category values.

        Returns:
            None
        """
        for category_name, category_value in categories.items():
            category_value = category_value(data) if callable(category_value) else category_value
            if not isinstance(category_value, (str, tuple, int, float)):
                raise TypeError(
                    f'Invalid category type for {category_name}: {type(category_value)}. '
                    'Expected str, tuple, int, or float.'
                )
            self[category_name].add(category_value, data)

    def collect(self, iterable: Iterable[VT_co], **categories: Category | Callable[[Iterable[VT_co]], Category]):
        """
        Collect values from the given iterable and add them to the appropriate categories in the collector.

        Args:
            iterable (Iterable[VT_co]): An iterable containing values to collect.
            **categories: Keyword arguments where keys are category names and values are either
                            category values or callables that return category values.

        Returns:
            None
        """
        # Optimization: If all categories are constant (not callables), we can use batch processing
        # This restores the O(1) Python overhead for Scenario 1 (Constant Category)
        if all(not callable(c) for c in categories.values()):
            # Convert iterable to tuple once if needed, or pass iterator if safe?
            # MappingCollector.add(*values) expects *args.
            # We must unpack. Unpacking an iterator consumes it.
            # If we have multiple categories, we need to reuse the data!
            # So we MUST materialize the iterable if there are multiple categories.

            # If iterable is already a sequence (list/tuple), fine.
            # If it's an iterator, we must listify it.
            values = tuple(iterable) if not isinstance(iterable, (list, tuple)) else iterable

            for category_name, category_value in categories.items():
                if not isinstance(category_value, (str, tuple, int, float)):
                    raise TypeError(
                        f'Invalid category type for {category_name}: {type(category_value)}. '
                        'Expected str, tuple, int, or float.'
                    )
                # Unpack the batch into add
                # We cast to Category because the static analyzer can't infer it from the isinstance check
                # when dealing with the TypeVar bound.
                self[category_name].add(cast(Category, category_value), *values)
            return

        # Fallback: Dynamic categories require item-by-item processing
        for data in iterable:
            self.add(data, **categories)


class CategoryCounter(CategoryCollector):
    def __init__(self, **kwargs: Any):
        """
        Initialize the CategoryCounter.
        """
        super().__init__(aggregation=Aggregation.COUNT, **kwargs)
