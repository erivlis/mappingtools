from enum import Enum

try:
    from warnings import deprecated
except ImportError:
    from deprecated import deprecated

from mappingtools.aggregation import Aggregation


@deprecated("AggregationMode is deprecated; use mappingtools.aggregation.Aggregation instead.")
class AggregationMode(Enum):
    """
    .. deprecated:: 0.8.0
       Use :class:`mappingtools.aggregation.Aggregation` instead.

    Define an enumeration class for data aggregation modes.
    """

    ALL = Aggregation.ALL
    COUNT = Aggregation.COUNT
    DISTINCT = Aggregation.DISTINCT
    FIRST = Aggregation.FIRST
    LAST = Aggregation.LAST
    SUM = Aggregation.SUM
    MAX = Aggregation.MAX
    MIN = Aggregation.MIN
    RUNNING_AVERAGE = Aggregation.RUNNING_AVERAGE
