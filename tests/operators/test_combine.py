import pytest

from mappingtools.operators import combine
from mappingtools.resolvers import LogicalResolver, NumericResolver, Resolver
from mappingtools.typing import MISSING


def test_combine_with_missing():
    # If one side is MISSING, the other wins regardless of resolver
    assert combine(1, MISSING, op=Resolver.FAIL) == 1
    assert combine(MISSING, 2, op=Resolver.FAIL) == 2


def test_combine_with_last_wins():
    # Should behave exactly like the default merge
    t1 = {"a": 1, "b": [1, 2]}
    t2 = {"a": 99, "b": [3]}

    result = combine(t1, t2, op=Resolver.LAST)
    assert result == {"a": 99, "b": [3, 2]}


def test_combine_with_first_wins():
    t1 = {"a": 1, "b": [1, 2]}
    t2 = {"a": 99, "b": [3]}

    result = combine(t1, t2, op=Resolver.FIRST)
    assert result == {"a": 1, "b": [1, 2]}


def test_combine_with_null():
    t1 = {"a": 1, "b": [1, 2]}
    t2 = {"a": 99, "b": [3]}

    result = combine(t1, t2, op=Resolver.NULL)
    assert result == {"a": None, "b": [None, 2]}


def test_combine_with_void():
    t1 = {"a": 1, "b": 2, "c": 3}
    # Conflict on 'a' and 'c'
    t2 = {"a": 99, "c": 33, "d": 4}

    result = combine(t1, t2, op=Resolver.VOID)

    # 'a' and 'c' are destroyed. 'b' and 'd' are kept.
    assert result == {"b": 2, "d": 4}


def test_combine_with_all():
    t1 = {"a": 1, "b": (1, 2)}
    t2 = {"a": 2, "b": 3}

    result = combine(t1, t2, op=Resolver.ALL)
    assert result == {"a": (1, 2), "b": (1, 2, 3)}


def test_combine_with_strict():
    t1 = {"a": 1, "b": 2}
    t2 = {"a": 1, "b": 3}

    # 'a' is identical, so it should resolve cleanly. 'b' conflicts and should fail.
    with pytest.raises(ValueError, match="Strict conflict detected"):
        combine(t1, t2, op=Resolver.STRICT)

    # If they are identical, it should succeed
    result = combine({"a": 1}, {"a": 1}, op=Resolver.STRICT)
    assert result == {"a": 1}


def test_combine_with_type_safe():
    t1 = {"port": 8080, "host": "localhost"}
    t2 = {"port": 9000, "host": "0.0.0.0"}

    # Types match, so the new values are accepted
    result = combine(t1, t2, op=Resolver.TYPE_SAFE)
    assert result == {"port": 9000, "host": "0.0.0.0"}

    # Now introduce a type violation
    t3 = {"port": "auto"}
    with pytest.raises(TypeError, match="Type strictness violated"):
        combine(t1, t3, op=Resolver.TYPE_SAFE)


def test_combine_with_mark():
    t1 = {"a": 1, "b": [1, 2]}
    t2 = {"a": 99, "b": [3]}

    result = combine(t1, t2, op=Resolver.MARK)
    assert result == {"a": {"__conflict__": (1, 99)}, "b": [{"__conflict__": (1, 3)}, 2]}


def test_combine_with_union():
    t1 = {"roles": frozenset(["admin"])}
    t2 = {"roles": "editor"}

    result = combine(t1, t2, op=Resolver.UNION)
    assert result == {"roles": frozenset(["admin", "editor"])}


def test_combine_with_coalesce():
    # first is truthy, it should win
    assert combine({"a": "john"}, {"a": ""}, op=Resolver.COALESCE) == {"a": "john"}
    # first is falsy, last should win
    assert combine({"a": ""}, {"a": "john"}, op=Resolver.COALESCE) == {"a": "john"}
    # both are falsy, last should win
    assert combine({"a": None}, {"a": 0}, op=Resolver.COALESCE) == {"a": 0}


def test_combine_with_logical_and():
    # Booleans
    assert combine({"a": True}, {"a": False}, op=LogicalResolver.AND) == {"a": False}
    # Bitmasks
    assert combine({"perms": 0b101}, {"perms": 0b011}, op=LogicalResolver.AND) == {"perms": 0b001}
    # Sets
    assert combine({"tags": {"A", "B"}}, {"tags": {"B", "C"}}, op=LogicalResolver.AND) == {"tags": {"B"}}


def test_combine_with_logical_or():
    # Booleans
    assert combine({"a": True}, {"a": False}, op=LogicalResolver.OR) == {"a": True}
    # Bitmasks
    assert combine({"perms": 0b100}, {"perms": 0b010}, op=LogicalResolver.OR) == {"perms": 0b110}
    # Sets
    assert combine({"tags": {"A"}}, {"tags": {"B"}}, op=LogicalResolver.OR) == {"tags": {"A", "B"}}


def test_combine_with_logical_xor():
    # Booleans
    assert combine({"a": True}, {"a": True}, op=LogicalResolver.XOR) == {"a": False}
    assert combine({"a": True}, {"a": False}, op=LogicalResolver.XOR) == {"a": True}
    # Bitmasks
    assert combine({"perms": 0b101}, {"perms": 0b011}, op=LogicalResolver.XOR) == {"perms": 0b110}
    # Sets (symmetric difference)
    assert combine({"tags": {"A", "B"}}, {"tags": {"B", "C"}}, op=LogicalResolver.XOR) == {"tags": {"A", "C"}}


def test_combine_with_sum():
    t1 = {"revenue": 100, "costs": {"q1": 50}}
    t2 = {"revenue": 200, "costs": {"q1": 60, "q2": 10}}

    result = combine(t1, t2, op=NumericResolver.SUM)
    assert result == {"revenue": 300, "costs": {"q1": 110, "q2": 10}}


def test_combine_with_mul():
    t1 = {"prob": {"p1": 0.8, "p2": 0.5}}
    t2 = {"prob": {"p1": 0.5, "p2": 0.5}}

    result = combine(t1, t2, op=NumericResolver.MUL)
    assert result == {"prob": {"p1": 0.4, "p2": 0.25}}


def test_combine_with_ema():
    t1 = {"temp": 40.0, "pressure": 100.0}
    t2 = {"temp": 42.0, "pressure": 110.0}

    # EMA interpolates: (old + new) * 0.5
    result = combine(t1, t2, op=NumericResolver.EMA)
    assert result == {"temp": 41.0, "pressure": 105.0}


def test_combine_with_min():
    t1 = {"revenue": 100, "costs": {"q1": 50}}
    t2 = {"revenue": 200, "costs": {"q1": 60, "q2": 10}}

    result = combine(t1, t2, op=NumericResolver.MIN)
    assert result == {"revenue": 100, "costs": {"q1": 50, "q2": 10}}


def test_combine_with_fail():
    t1 = {"a": 1}
    t2 = {"a": 2}

    with pytest.raises(ValueError, match="Trees must be structurally mutually exclusive"):
        combine(t1, t2, op=Resolver.FAIL)


def test_combine_structural_conflict_dict_vs_list():
    t1 = {"a": {"nested": 1}}
    t2 = {"a": [1, 2, 3]}

    # LAST wins should completely overwrite the dict with the list
    assert combine(t1, t2, op=Resolver.LAST) == {"a": [1, 2, 3]}

    # FIRST wins should keep the dict
    assert combine(t1, t2, op=Resolver.FIRST) == {"a": {"nested": 1}}

    # FAIL should raise an error because they are fundamentally different structures
    with pytest.raises(ValueError):
        combine(t1, t2, op=Resolver.FAIL)


def test_combine_with_custom_callable():
    t1 = {"tags": "urgent"}
    t2 = {"tags": "backend"}

    # Custom callable that joins strings with a comma
    result = combine(t1, t2, op=lambda a, b: f"{a},{b}")
    assert result == {"tags": "urgent,backend"}


def test_combine_deep_nested_conflict():
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
    result = combine(t1, t2, op=NumericResolver.MAX)
    assert result == {
        "user": {
            "profile": {
                "age": 35,
                "score": 100,
                "visits": 5
            }
        }
    }
