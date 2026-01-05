import math
from typing import Protocol, TypeVar

V = TypeVar('V')

__all__ = [
    'BooleanSemiring',
    'BottleneckSemiring',
    'LogSemiring',
    'ReliabilitySemiring',
    'Semiring',
    'StandardSemiring',
    'StringSemiring',
    'TropicalSemiring',
    'ViterbiSemiring',
]


class Semiring(Protocol[V]):
    """
    A Protocol defining a Semiring (S, +, *, 0, 1).
    Used to generalize linear algebra operations.
    """

    @property
    def zero(self) -> V:
        """The additive identity element (e.g., 0)."""
        ...

    @property
    def one(self) -> V:
        """The multiplicative identity element (e.g., 1)."""
        ...

    def add(self, a: V, b: V) -> V:
        """The addition operation (commutative, associative)."""
        ...

    def mul(self, a: V, b: V) -> V:
        """The multiplication operation (associative, distributes over add)."""
        ...


class StandardSemiring:
    """
    The standard algebra over real numbers.
    (R, +, *, 0, 1)
    Used for: Standard Linear Algebra, Physics.
    """

    @property
    def zero(self) -> float:
        return 0.0

    @property
    def one(self) -> float:
        return 1.0

    @staticmethod
    def add(a: float, b: float) -> float:
        return a + b

    @staticmethod
    def mul(a: float, b: float) -> float:
        return a * b


class TropicalSemiring:
    """
    The Min-Plus algebra.
    (R U {inf}, min, +, inf, 0)
    Used for: Shortest Path problems (Graph Theory).
    """

    @property
    def zero(self) -> float:
        return float('inf')

    @property
    def one(self) -> float:
        return 0.0

    @staticmethod
    def add(a: float, b: float) -> float:
        return min(a, b)

    @staticmethod
    def mul(a: float, b: float) -> float:
        return a + b


class BooleanSemiring:
    """
    The Boolean algebra.
    ({T, F}, OR, AND, F, T)
    Used for: Reachability, Transitive Closure.
    """

    @property
    def zero(self) -> bool:
        return False

    @property
    def one(self) -> bool:
        return True

    @staticmethod
    def add(a: bool, b: bool) -> bool:
        return a or b

    @staticmethod
    def mul(a: bool, b: bool) -> bool:
        return a and b


class ViterbiSemiring:
    """
    The Max-Product algebra.
    ([0, 1], max, *, 0, 1)
    Used for: Most Likely Path (HMMs).
    """

    @property
    def zero(self) -> float:
        return 0.0

    @property
    def one(self) -> float:
        return 1.0

    @staticmethod
    def add(a: float, b: float) -> float:
        return max(a, b)

    @staticmethod
    def mul(a: float, b: float) -> float:
        return a * b


class ReliabilitySemiring(ViterbiSemiring):
    """
    Alias for ViterbiSemiring.
    Used for: Reliability analysis (max probability path).
    """


class BottleneckSemiring:
    """
    The Max-Min algebra.
    (R, max, min, -inf, +inf)
    Used for: Maximum Capacity Path (Widest Path).
    """

    @property
    def zero(self) -> float:
        return float('-inf')

    @property
    def one(self) -> float:
        return float('inf')

    @staticmethod
    def add(a: float, b: float) -> float:
        return max(a, b)

    @staticmethod
    def mul(a: float, b: float) -> float:
        return min(a, b)


class LogSemiring:
    """
    The Log-Sum-Exp algebra.
    (R U {-inf}, logaddexp, +, -inf, 0)
    Used for: Probabilistic inference in log-domain (avoids underflow).
    Values represent log-probabilities.
    """

    @property
    def zero(self) -> float:
        return float('-inf')

    @property
    def one(self) -> float:
        return 0.0

    @staticmethod
    def add(a: float, b: float) -> float:
        # log(exp(a) + exp(b))
        if a == float('-inf'):
            return b
        if b == float('-inf'):
            return a

        # Numerical stability: log(exp(a) + exp(b)) = max + log(exp(a-max) + exp(b-max))
        max_val = max(a, b)
        return max_val + math.log(math.exp(a - max_val) + math.exp(b - max_val))

    @staticmethod
    def mul(a: float, b: float) -> float:
        # log(exp(a) * exp(b)) = a + b
        return a + b


class StringSemiring:
    """
    The Formal Language algebra.
    (P(Sigma*), Union, Concatenation, {}, {""})
    Used for: Regular Expressions, Path Languages.
    Values are Sets of Strings.
    """

    @property
    def zero(self) -> set[str]:
        return set()

    @property
    def one(self) -> set[str]:
        return {''}

    @staticmethod
    def add(a: set[str], b: set[str]) -> set[str]:
        return a | b

    @staticmethod
    def mul(a: set[str], b: set[str]) -> set[str]:
        # Concatenation of sets: {xy | x in a, y in b}
        if not a or not b:
            return set()
        return {x + y for x in a for y in b}
