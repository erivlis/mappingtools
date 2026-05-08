import pytest

from mappingtools.operators import lift
from mappingtools.resolvers import Resolver
from mappingtools.typing import MISSING


def test_lift_with_missing():
    # If one side is MISSING, the other wins regardless of resolver
    assert lift(1, MISSING, op=Resolver.FAIL) == 1
    assert lift(MISSING, 2, op=Resolver.FAIL) == 2


def test_lift_with_last_wins():
    # Should behave exactly like the default merge
    t1 = {"a": 1, "b": [1, 2]}
    t2 = {"a": 99, "b": [3]}

    result = lift(t1, t2, op=Resolver.LAST)
    assert result == {"a": 99, "b": [3, 2]}


def test_lift_with_first_wins():
    t1 = {"a": 1, "b": [1, 2]}
    t2 = {"a": 99, "b": [3]}

    result = lift(t1, t2, op=Resolver.FIRST)
    assert result == {"a": 1, "b": [1, 2]}


def test_lift_with_sum():
    t1 = {"revenue": 100, "costs": {"q1": 50}}
    t2 = {"revenue": 200, "costs": {"q1": 60, "q2": 10}}

    result = lift(t1, t2, op=Resolver.SUM)
    assert result == {"revenue": 300, "costs": {"q1": 110, "q2": 10}}


def test_lift_with_fail():
    t1 = {"a": 1}
    t2 = {"a": 2}

    with pytest.raises(ValueError, match="Conflict detected at leaf"):
        lift(t1, t2, op=Resolver.FAIL)


def test_lift_structural_conflict_dict_vs_list():
    t1 = {"a": {"nested": 1}}
    t2 = {"a": [1, 2, 3]}

    # LAST wins should completely overwrite the dict with the list
    assert lift(t1, t2, op=Resolver.LAST) == {"a": [1, 2, 3]}

    # FIRST wins should keep the dict
    assert lift(t1, t2, op=Resolver.FIRST) == {"a": {"nested": 1}}

    # FAIL should raise an error because they are fundamentally different structures
    with pytest.raises(ValueError):
        lift(t1, t2, op=Resolver.FAIL)


def test_lift_with_custom_callable():
    t1 = {"tags": "urgent"}
    t2 = {"tags": "backend"}

    # Custom callable that joins strings with a comma
    result = lift(t1, t2, op=lambda a, b: f"{a},{b}")
    assert result == {"tags": "urgent,backend"}


def test_lift_deep_nested_conflict():
    t1 = {
        "user": {
            "profile": {
                "age": 30,
                "score": 100
            }
        }
    }
    t2 = {
        "user": {
            "profile": {
                "age": 35,
                "visits": 5
            }
        }
    }

    # Max aggregation
    result = lift(t1, t2, op=Resolver.MAX)
    assert result == {
        "user": {
            "profile": {
                "age": 35,
                "score": 100,
                "visits": 5
            }
        }
    }
