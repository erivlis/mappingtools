import operator
from enum import Enum

try:
    from enum import member
except ImportError:
    class member:  # noqa: N801 this is for python <3.11
        """
        Forces item to become an Enum member during class creation.
        """

        def __init__(self, value):
            self.value = value

        def __call__(self, *args, **kwargs):
            return self.value(*args, **kwargs)

from typing import Any


def _fail_resolver(first: Any, last: Any) -> Any:
    """Raise a ValueError on any conflict."""
    raise ValueError(f"Conflict detected at leaf. Old: {first}, New: {last}")


def _first_resolver(first: Any, last: Any) -> Any:
    return first


def _last_resolver(first: Any, last: Any) -> Any:
    return last


class Resolver(Enum):
    """
    Defines a strategy for resolving a conflict between two scalar values during a merge.
    """

    FAIL = member(_fail_resolver)
    """Raise a ValueError on any conflict."""

    FIRST = member(_first_resolver)
    """Keep the original value in a conflict."""

    LAST = member(_last_resolver)
    """Overwrite the original value with the new one."""


class NumericResolver(Enum):
    MAX = member(max)
    """Take the maximum of the old and new values."""

    MIN = member(min)
    """Take the minimum of the old and new values."""

    SUM = member(operator.add)
    """Sum the old and new values in a conflict."""


ResolverType = Resolver | NumericResolver
