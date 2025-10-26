import functools
from collections import defaultdict, deque
from collections.abc import Callable
from datetime import datetime, timedelta
from enum import Flag, auto
from typing import Any

from mappingtools._compat import UTC
from mappingtools.typing import KT, VT_co


class DictOperation(Flag):
    """
    An enumeration class for tracking categories.
    """
    GET = auto()
    GET_DEFAULT = auto()
    SET = auto()
    SET_DEFAULT = auto()
    POP = auto()

    @property
    def repr_name(self) -> str:
        return (self.name or '').casefold()

    @classmethod
    def atomic_operations(cls, operations: 'DictOperation') -> list['DictOperation']:
        return [o for o in DictOperation if o & operations]


class TimeSeries:
    """
    A class to track access times and statistics.

    Attributes:
        count (int): The number of times the key has been accessed.
        first (datetime | None): The timestamp of the first access.
        last (datetime | None): The timestamp of the last access.

    Methods:
        add(dt: datetime | None = None): Records a TimeSeries entry at the specified datetime.
        reset(): Resets the TimeSeries to its initial state.
        duration() -> timedelta: Returns the duration between the first and last access times.
        duration_cma(weights: tuple | None) -> float: Returns the weighted moving average duration between accesses.
        frequency() -> float: Returns the frequency of accesses per second.
        summary() -> dict[str, Any]: Returns a summary of TimeSeries statistics.
        values() -> list[datetime]: Returns a list of recorded access timestamps.
        durations() -> list[timedelta]: Returns a list of durations between consecutive accesses.

    """

    def __init__(self, samples_counts: int = 2):

        if samples_counts < 2:
            raise ValueError("samples_counts must be at least 2")

        self._samples_count = samples_counts
        self._series: deque[datetime] = deque(maxlen=samples_counts)
        self._durations: deque[timedelta] = deque(maxlen=samples_counts - 1)

        self.count: int = 0

        self.first: datetime | None = None
        self.last: datetime | None = None

    def add(self, dt: datetime | None = None):
        """
        Records a TimeSeries entry at the specified datetime.
        If no datetime is provided, the current UTC time is used.
        """
        if dt is None:
            dt = datetime.now(tz=UTC)

        self.count += 1

        self._series.append(dt)
        if len(self._series) > 1:
            self._durations.append(dt - self._series[-2])

        if self.count == 1:
            self.first = dt
        self.last = dt

    def reset(self):
        """Resets the TimeSeries to its initial state."""
        self.__init__(self._samples_count)

    def duration(self) -> timedelta:
        """
        Returns the duration between the first and last access times.
        If no access has been recorded, it returns 0.0.
        """
        return self.last - self.first if all((self.first, self.last)) else timedelta()

    def duration_cma(self, weights: tuple | None) -> float:
        """
        Returns the weighted moving average duration between accesses.
        If no durations are recorded, returns 0.0.

        Args:
            weights (tuple | None): A tuple of weights for the moving average calculation.
                                    If None, equal weights are used.

        Returns:
            float: The weighted moving average duration in seconds.
        """

        if weights is None:
            weights = (1,) * (self._samples_count - 1)

        if len(weights) != self._samples_count - 1:
            raise ValueError("Weights length must match times series' count-1")

        if self._durations is None:
            return 0.0

        effective_weights = weights[-len(self._durations):]
        total_weights = sum(effective_weights)
        return sum(w * d.total_seconds() for w, d in zip(effective_weights, self._durations)) / total_weights

    def durations(self) -> list[timedelta]:
        return list(self._durations)

    def frequency(self) -> float:
        """
        Returns the frequency of accesses per second.
        If the access count is 0 or 1, returns 0.0.

        Returns:
            float: The frequency of accesses per second.
        """
        if self.count <= 1:
            return 0.0
        duration_seconds = self.duration().total_seconds()
        return self.count / duration_seconds if duration_seconds > 0 else 0.0

    def summary(self) -> dict[str, Any]:
        """
        Returns a summary of TimeSeries, including count, first and last access times,
        duration, frequency, moving average duration, and moving average frequency.

        Returns:
            dict[str, Any]: A dictionary containing the summary of the TimeSeries.
        """

        output = {
            'count': self.count,
            'first': self.first,
            'last': self.last,
            'duration': self.duration(),
            'frequency': self.frequency(),
        }

        return output

    def values(self) -> list[datetime]:
        return list(self._series)


class MeteredDict(dict[KT, VT_co]):
    """
    A dictionary that tracks access and modification statistics for its keys.
    """
    _default_operations: DictOperation = (
            DictOperation.GET
            | DictOperation.GET_DEFAULT
            | DictOperation.SET
            | DictOperation.SET_DEFAULT
            | DictOperation.POP
    )

    def __init__(self, operations: DictOperation | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._operations: DictOperation = operations or self._default_operations
        self._metering: dict[DictOperation, defaultdict[str, TimeSeries]] = {
            o: defaultdict(TimeSeries, **kwargs) for o in self.operations
        }

    def _atomic_operations(self, operations: DictOperation) -> list[DictOperation]:
        """Returns the list of atomic operations from the configured operations that are being tracked."""
        actual_operations = DictOperation.atomic_operations(operations & self._operations)

        if actual_operations:
            return actual_operations
        else:
            raise ValueError("No valid operations to track.")

    @functools.cached_property
    def operations(self) -> list[DictOperation]:
        """Returns the list of active operations being tracked."""
        return self._atomic_operations(self._operations)

    def _add(self, key: KT, operations: DictOperation):
        """
        Increment the tracking information for the specified key and operations.
        """
        if operations in self._metering:
            self._metering[operations][key].add()

    def __getitem__(self, key: KT) -> VT_co:
        self._add(key, DictOperation.GET)
        return super().__getitem__(key)

    def __setitem__(self, key: KT, value: VT_co):
        self._add(key, DictOperation.SET)
        super().__setitem__(key, value)

    def get(self, key: KT, default: VT_co = None) -> VT_co:
        """
        Returns the value for the specified key if it exists, otherwise returns the default value.
        If the key does not exist, it increments the default access count.
        """
        try:
            value = super().__getitem__(key)
            self._add(key, DictOperation.GET)
        except KeyError:
            value = default
            self._add(key, DictOperation.GET_DEFAULT)
        return value

    def pop(self, key: KT) -> VT_co:
        self._add(key, DictOperation.POP)
        return super().pop(key)

    def popitem(self) -> tuple[KT, VT_co]:
        key, value = super().popitem()
        self._add(key, DictOperation.POP)
        return key, value

    def setdefault(self, key: KT, default: VT_co = None) -> VT_co:
        """
        Returns the value for the specified key if it exists, otherwise sets it to the default value.
        If the key does not exist, it increments the default access count.
        """
        if key not in self:
            self._add(key, DictOperation.SET_DEFAULT)
            super().__setitem__(key, default)

        return default

    def _invoke(
            self,
            func: Callable[[TimeSeries], Any],
            key: KT,
            operations: DictOperation | None = None
    ) -> dict[str, Any]:
        return {
            o.repr_name: func(self._metering[o][key])
            for o in (self.operations if operations is None else self._atomic_operations(operations))
        }

    def count(self, key: KT, operations: DictOperation | None = None) -> dict[str, int]:
        """
        Returns the number of times a key has been accessed.

        Args:
            key (KT): The key to check access count for.
            operations (DictOperation): The operation of tracking to check.

        """
        return self._invoke(lambda ts: ts.count, key, operations)

    def counts(self, operations: DictOperation | None = None) -> dict[KT, dict[str, int]]:
        """
        Returns a summary of access counts for all keys in the dictionary.

        Returns:
            dict[KT, dict[str, int]]: A dictionary containing access counts for each key.
        """
        return {k: self.count(k, operations) for k in self}

    def frequency(self, key: KT, operations: DictOperation | None = None) -> dict[str, float]:
        """
        Returns the frequency of access for a key.

        Args:
            key (KT): The key to check access frequency for.
            operations (DictOperation | None): The operation to check. If None, checks all operations.

        Returns:
            float: The frequency of access for the key.
        """
        return self._invoke(lambda ts: ts.frequency(), key, operations)

    def frequencies(self, operations: DictOperation | None = None) -> dict[KT, dict[str, float]]:
        """
        Returns a summary of access frequencies for all keys in the dictionary.

        Returns:
            dict[KT, dict[str, float]]: A dictionary containing access frequencies for each key.
        """
        return {k: self.frequency(k, operations) for k in self}

    def summary(self, key: KT, operations: DictOperation | None = None) -> dict[str, Any]:
        """
        Returns a summary of access information for each k in the dictionary.

        Returns:
            dict[KT, dict[str, Any]]: A dictionary containing access information for each k.
        """
        return self._invoke(lambda ts: ts.summary(), key, operations)

    def summaries(self, operations: DictOperation | None = None) -> dict[KT, dict[str, Any]]:
        """
        Returns a summary of access information for all keys in the dictionary.

        Returns:
            dict[KT, dict[str, Any]]: A dictionary containing access information for each key.
        """
        return {k: self.summary(k, operations) for k in self}

    def filter_keys(self,
                    predicate: Callable[[KT, DictOperation], bool],
                    operations: DictOperation | None = None) -> list[KT]:
        return [
            k for k in self
            for o in (self.operations if operations is None else self._atomic_operations(operations))
            if predicate(k, o)
        ]

    def used_keys(
            self,
            min_count: int = 0,
            max_count: int = float('inf'),
            min_frequency: float = 0.0,
            max_frequency: float = float('inf'),
            before: datetime | None = None,
            after: datetime | None = None,
            operations: DictOperation | None = None
    ) -> list[KT]:
        """
        Returns a list of keys that have been accessed at least once.

        Args:
            min_count (int): Minimum number of accesses for the key to be included (default is 0).
            max_count (int): Maximum number of accesses for the key to be included (default is float('inf')).
            min_frequency (float): Minimum frequency of access for the key to be included (default is 0.0).
            max_frequency (float): Maximum frequency of access for the key to be included (default is float('inf')).
            before (datetime | None):
                If specified, only keys accessed before this datetime will be included (default is None).
            after (datetime | None):
                If specified, only keys accessed after this datetime will be included (default is None).
            operations (DictOperation | None): The operation to check. If None, checks all operations.

        Returns:
            list[KT]: A list of keys that have been accessed.
        """

        def _predicate(k: KT, o: DictOperation) -> bool:
            ts = self._metering[o][k]
            return (min_count < ts.count < max_count
                    and min_frequency <= ts.frequency() <= max_frequency
                    and (before is None or ts.last < before)
                    and (after is None or ts.first > after))

        return self.filter_keys(_predicate, operations)

    def unused_keys(
            self,
            operations: DictOperation | None = None
    ) -> list[KT]:
        """
        Returns a list of keys that have never been accessed.

        Args:
            operations (DictOperation | None): The operation to check. If None, checks all operations.

        Returns:
            list[KT]: A list of keys that have never been accessed.
        """

        def _predicate(k: KT, o: DictOperation) -> bool:
            ts = self._metering[o][k]
            return ts.count == 0

        return self.filter_keys(_predicate, operations)

    def _reset(self, key: KT, operation: DictOperation):
        """Resets the tracking information for the specified operation and key."""
        self._metering.get(operation, {})[key].reset()

    def reset(self, key: KT | None = None, operations: DictOperation | None = None):
        """
        Resets the tracking information for the specified operation and key.

        Args:
            key (KT | None): The key to reset tracking information for (default is None, which resets all keys).
            operations (DictOperation | None): The operations to reset (default is None, which resets all).

        Returns:
            None
        """
        for o in self._atomic_operations(operations) if operations else self.operations:
            if key is None:
                for k in self._metering[o]:
                    self._reset(k, o)
            else:
                self._reset(key, o)
