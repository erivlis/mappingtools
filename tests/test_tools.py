import dataclasses
import math

import pytest

from mappingtools._tools import (
    StringArrangements,
    _is_class_instance,
    _is_strict_iterable,
    probabilities,
    shannon_entropy,
)


def test_is_strict_iterable_and_bytes_handling():
    # Arrange
    seq = [1, 2, 3]
    gen = (x for x in [1])
    s = "abc"
    b = b"abc"
    ba = bytearray(b"abc")

    # Act / Assert
    assert _is_strict_iterable(seq) is True
    assert _is_strict_iterable(gen) is True
    assert _is_strict_iterable(s) is False
    assert _is_strict_iterable(b) is False
    assert _is_strict_iterable(ba) is False


def test_is_class_instance_dataclass_and_object():
    # Arrange
    @dataclasses.dataclass
    class DC:
        x: int

    class C:
        def __init__(self):
            self.y = 1

    # Act / Assert
    assert _is_class_instance(DC(1)) is True
    assert _is_class_instance(C()) is True
    # The implementation treats dataclass *classes* as having a __dict__,
    # so this returns True (matches current behavior).
    assert _is_class_instance(DC) is True
    assert _is_class_instance(123) is False


def test_string_arrangements_of_and_count_and_of_invalid_length():
    # Arrange
    sa = StringArrangements("AB")

    # Act
    count = sa.count_of(2)
    got = list(sa.of(2))

    # Assert
    assert count == 4
    assert got == ["AA", "AB", "BA", "BB"]

    # Arrange (invalid)
    gen = sa.of(0)
    # Act / Assert
    with pytest.raises(ValueError):
        next(gen)


def test_stream_basic_and_invalid_count():
    # Arrange
    sa = StringArrangements("AB")

    # Act
    gen = sa.stream(3)
    out = [next(gen) for _ in range(3)]

    # Assert
    assert out == ["A", "B", "AA"]

    # Arrange (invalid)
    gen_bad = sa.stream(0)
    # Act / Assert
    with pytest.raises(ValueError):
        next(gen_bad)


def test_uniform_distribution_and_weighted_distribution_behaviour():
    # Arrange
    sa = StringArrangements("ABC")
    sa2 = StringArrangements("AB")
    weights = {"A": 2, "B": 1}

    # Act
    uniform = sa.uniform_distribution_of(2)
    weighted = sa2.weighted_distribution_of(1, weights)

    # Assert
    assert uniform('XX') == pytest.approx(1 / 9)
    # For 'A': total_weight=3, distribution uniform=1/2 -> 3*(1/2)*2 = 3
    assert weighted('A') == pytest.approx(3.0)
    # According to implementation: total_weight=3, uniform=1/2 -> 3*(1/2)*1 = 1.5
    assert weighted('B') == pytest.approx(1.5)
    # missing key returns 0.0
    assert weighted('C') == pytest.approx(0.0)

    # Act / Assert: total weight <= 0 should raise
    with pytest.raises(ValueError):
        sa2.weighted_distribution_of(1, {"A": 0, "B": 0})


def test_probabilities_uniform_and_weighted():
    # Arrange

    # Act
    probs = list(probabilities(1, alphabet="AB"))
    probs_w = list(probabilities(1, alphabet="AB", weights={"A": 2}))

    # Assert
    assert probs == [pytest.approx(0.5), pytest.approx(0.5)]
    # Use the same logic as weighted_distribution_of: total_weight=2, distribution uniform=1/2
    # for 'A' -> 2*(1/2)*2 = 2.0 ; for 'B' -> 0.0
    assert probs_w[0] == pytest.approx(2.0)
    assert probs_w[1] == pytest.approx(0.0)


def test_shannon_entropy_uniform_matches_log_of_outcomes():
    # Arrange

    # Act
    ent = shannon_entropy(2, alphabet="AB")

    # Assert
    assert ent == pytest.approx(math.log(4))


def test_string_arrangements_classmethods():
    # Arrange
    import string as _s

    # Act / Assert
    assert StringArrangements.ascii_uppercase().alphabet == _s.ascii_uppercase
    assert StringArrangements.ascii_lowercase().alphabet == _s.ascii_lowercase
    assert StringArrangements.ascii_letters().alphabet == _s.ascii_letters
    assert StringArrangements.ascii_digits().alphabet == _s.digits
    assert StringArrangements.hex_digits().alphabet == _s.hexdigits
    assert StringArrangements.oct_digits().alphabet == _s.octdigits


def test_stream_full_length_iteration_behaviour():
    # Arrange
    sa = StringArrangements("AB")

    # Act
    out = list(sa.stream(4))

    # Assert
    assert out == ["A", "B", "AA", "AB"]


def test_call_classmethods_via_func_object():
    # Arrange
    names = [
        'ascii_uppercase', 'ascii_lowercase', 'ascii_letters', 'ascii_digits', 'hex_digits', 'oct_digits'
    ]

    # Act / Assert
    for name in names:
        cm = StringArrangements.__dict__[name]
        # cm is a function wrapped as classmethod; call the underlying function with the class
        res = cm.__func__(StringArrangements)
        assert isinstance(res, StringArrangements)


def test_stream_break_condition_is_hit():
    # Arrange
    sa = StringArrangements("AB")

    # Act
    gen = sa.stream(2)
    first = next(gen)
    second = next(gen)

    # Assert
    assert [first, second] == ["A", "B"]


def test_probabilities_with_distribution_and_weights():
    # Arrange
    alphabet = "AB"
    length = 1

    def dist(s: str) -> float:
        return 0.1 if s == 'A' else 0.9

    weights = {'A': 1, 'B': 2}

    # Act
    probs = list(probabilities(length, alphabet=alphabet, distribution=dist, weights=weights))

    # Assert
    # weighted_distribution_of calculates: total_weight * distribution(s) * w
    # total_weight = 3 -> for A: 3 * 0.1 * 1 = 0.3 ; for B: 3 * 0.9 * 2 = 5.4
    assert pytest.approx(0.3) == probs[0]
    assert pytest.approx(5.4) == probs[1]


def test_probabilities_with_only_distribution_provided():
    # Arrange
    def dist(s: str) -> float:
        return 0.7 if s == 'A' else 0.3

    # Act
    probs = list(probabilities(1, alphabet='AB', distribution=dist))

    # Assert
    assert probs[0] == pytest.approx(0.7)
    assert probs[1] == pytest.approx(0.3)
