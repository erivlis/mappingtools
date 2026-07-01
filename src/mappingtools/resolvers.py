import operator
from enum import Enum
from typing import Any, Protocol, cast

from mappingtools.typing import MISSING, T, Tree

try:
    from enum import member
except ImportError:  # pragma: no cover
    class member:  # noqa: N801 this is for python <3.11
        """
        Forces item to become an Enum member during class creation.
        """

        def __init__(self, value):
            self.value = value

        def __call__(self, *args, **kwargs):
            return self.value(*args, **kwargs)


# region Resolvers

def _all_resolver(first: Any, last: Any) -> Any:
    """Keep both values as a tuple in a conflict.
    If either value is already a tuple, we will not nest it further but just combine them into a single flat tuple."""
    first_tuple = first if isinstance(first, tuple) else (first,)
    last_tuple = last if isinstance(last, tuple) else (last,)
    return first_tuple + last_tuple


def _coalesce_first_resolver(first: Any, last: Any) -> Any:
    """Return the first if it is not None otherwise return the last value."""
    return last if first is None else first


def _coalesce_last_resolver(first: Any, last: Any) -> Any:
    """Return the last if it is not None otherwise return the first value."""
    return first if last is None else last


def _fail_resolver(first: Any, last: Any) -> Any:
    """Raise a ValueError on any conflict."""
    raise ValueError(f"Trees must be structurally mutually exclusive. Conflict at leaf. Old: {first}, New: {last}")


def _first_resolver(first: Any, _: Any) -> Any:
    return first


def _last_resolver(_: Any, last: Any) -> Any:
    return last


def _mark_resolver(first: Any, last: Any) -> dict[str, Any]:
    """Defer the conflict by returning a marked dictionary containing both values."""
    return {"__conflict__": (first, last)}


def _null_resolver(_: Any, __: Any) -> Any:
    """Always return None on a conflict."""
    return None


def _prefer_first_resolver(first: Any, last: Any) -> Any:
    """Return the first if it is a truthy value, otherwise return the last value."""

    if isinstance(first, bool) and isinstance(last, bool):
        # Special case for booleans: prefer True over False
        return first

    return first or last


def _prefer_last_resolver(first: Any, last: Any) -> Any:
    """Return the last if it is a truthy value, otherwise return the first value."""

    if isinstance(first, bool) and isinstance(last, bool):
        # Special case for booleans: prefer True over False
        return last

    return last or first


def _strict_resolver(first: Any, last: Any) -> Any:
    """Return the value if both are identical, otherwise raise a ValueError."""
    if first == last:
        return first
    raise ValueError(f"Strict conflict detected at leaf. Old: {first}, New: {last}")


def _type_safe_resolver(first: Any, last: Any) -> Any:
    """Return the new value if it shares the exact same type as the old value, otherwise raise a TypeError."""
    if type(first) is type(last):
        return last
    raise TypeError(f"Type strictness violated at leaf. Expected {type(first).__name__}, got {type(last).__name__}")


def _union_resolver(first: Any, last: Any) -> frozenset[Any]:
    """Combine both values into a frozenset.
    If either value is already a frozenset, unpack it into the new set."""
    first_set = first if isinstance(first, frozenset) else frozenset([first])
    last_set = last if isinstance(last, frozenset) else frozenset([last])
    return first_set | last_set


def _void_resolver(_: Any, __: Any) -> Any:
    """Always return MISSING on a conflict, which will cause the key to be removed from the result."""
    return MISSING


class Resolver(Enum):
    """
    Defines a strategy for resolving a conflict between two scalar values during a merge.
    """
    ALL = member(_all_resolver)
    """Combine both values into a flat tuple."""

    COALESCE_FIRST = member(_coalesce_first_resolver)
    """Return the first value if it is not None, otherwise return the last value."""

    COALESCE_LAST = member(_coalesce_last_resolver)
    """Return the last value if it is not None, otherwise return the first value."""

    FAIL = member(_fail_resolver)
    """Raise a ValueError blindly on any intersection, enforcing that the trees are structurally mutually exclusive."""

    FIRST = member(_first_resolver)
    """Keep the original value in a conflict."""

    LAST = member(_last_resolver)
    """Overwrite the original value with the new one."""

    MARK = member(_mark_resolver)
    """Defer the conflict by returning a dictionary tagged with '__conflict__'."""

    NULL = member(_null_resolver)
    """Always return None on a conflict."""

    PREFER_FIRST = member(_prefer_first_resolver)
    """Return the first if it is a truthy value, otherwise return the last value."""

    PREFER_LAST = member(_prefer_last_resolver)
    """Return the last if it is a truthy value, otherwise return the first value."""

    STRICT = member(_strict_resolver)
    """Return the value if both are identical, otherwise raise a ValueError."""

    TYPE_SAFE = member(_type_safe_resolver)
    """Accept the new value only if it shares the exact same type as the original value, otherwise raise a TypeError."""

    UNION = member(_union_resolver)
    """Combine both values into a flat frozenset."""

    VOID = member(_void_resolver)
    """Always return MISSING on a conflict, which will cause the key to be removed from the result."""


class LogicalResolver(Enum):
    AND = member(operator.and_)
    """Take the logical AND of the old and new values (supports booleans, bitmasks, and sets)."""

    OR = member(operator.or_)
    """Take the logical OR of the old and new values (supports booleans, bitmasks, and sets)."""

    XOR = member(operator.xor)
    """Take the logical XOR of the old and new values (supports booleans, bitmasks, and sets)."""


def _ema_resolver(first: Any, last: Any) -> Any:
    """Calculate the exponential moving average (alpha=0.5) of the old and new values."""
    return (first + last) * 0.5


class NumericResolver(Enum):
    MAX = member(max)
    """Take the maximum of the old and new values."""

    MIN = member(min)
    """Take the minimum of the old and new values."""

    MUL = member(operator.mul)
    """Multiply the old and new values in a conflict."""

    SUM = member(operator.add)
    """Sum the old and new values in a conflict."""

    EMA = member(_ema_resolver)
    """Calculate the exponential moving average (alpha=0.5) of the old and new values."""


ResolverType = Resolver | LogicalResolver | NumericResolver


# endregion Resolvers

# region Decision Metrics

class DecisionMetricOperator(Protocol):

    def __call__(self, t1: Any, t2: Any, resolved: Any) -> Any:
        ...


def _audit_metric(t1: Any, t2: Any, resolved: Any) -> str:
    if t1 is MISSING or t2 is MISSING:
        return "clean"
    if t1 == t2:
        return "clean"
    return f"conflict: `{t1}` vs `{t2}` -> `{resolved}`"


def _change_metric(t1: Any, t2: Any, resolved: Any) -> str:
    """Determine the change status of the resolved value."""
    if t1 is MISSING:
        return "added"
    if t2 is MISSING:
        return "unchanged"
    if resolved == t1:
        return "unchanged"
    return "updated"


def _provenance_metric(t1: Any, t2: Any, resolved: Any) -> int | None:
    """
    Determine the provenance of the resolved value based on its origin.
    """
    if t1 is MISSING:
        return 1
    if t2 is MISSING:
        return 0
    if type(resolved) is type(t1) and resolved == t1:
        return 0
    if type(resolved) is type(t2) and resolved == t2:
        return 1
    return None


class DecisionMetric(Enum):
    """
    Decision metrics are used to evaluate the outcome of a merge operation,
    providing insights into the nature of the resolution.
    """

    AUDIT = member(_audit_metric)
    """Produces 'clean' or a conflict description string at conflict leaves."""

    CHANGELOG = member(_change_metric)
    """Produces 'added', 'updated', or 'unchanged' relative to tree1."""

    PROVENANCE = member(_provenance_metric)
    """Produces 0 (tree1 wins), 1 (tree2 wins), or None (aggregative/composite) at conflict leaves."""

    @classmethod
    def _calculate(cls, x: Any, side: int, decision_operator: DecisionMetricOperator | None) -> Any:
        if isinstance(x, dict):
            return {k: (MISSING if v is MISSING else cls._calculate(v, side, decision_operator)) for k, v in
                    x.items()}
        elif isinstance(x, list):
            return [(MISSING if v is MISSING else cls._calculate(v, side, decision_operator)) for v in x]
        else:
            if callable(decision_operator):
                return decision_operator(x, MISSING, x) if side == 0 else decision_operator(MISSING, x, x)
            return None

    @classmethod
    def calculate(
            cls,
            combined_tree: Tree[Any],
            side: int,
            decision_op: DecisionMetricOperator | None = None
    ) -> Tree[Any]:
        return cls._calculate(combined_tree, side=side, decision_operator=decision_op)

    def of(self, combined_tree: Tree[T], side: int) -> Tree[Any]:
        decision_op: DecisionMetricOperator = cast(DecisionMetricOperator, self.value)
        return self.calculate(combined_tree, side, decision_op)

    @classmethod
    def nullify(cls, combined_tree: Tree[T]) -> Tree[Any]:
        return cls.calculate(combined_tree, side=0)

# endregion Decision Metrics
