from mappingtools.operators import combine
from mappingtools.resolvers import DecisionMetric, NumericResolver, Resolver


def test_combine_with_provenance_single_metric():
    t1 = {"a": 1, "b": [10, 20]}
    t2 = {"a": 99, "b": [30]}

    combined, metrics = combine(t1, t2, Resolver.LAST, [DecisionMetric.PROVENANCE])
    assert combined == {"a": 99, "b": [30, 20]}
    assert metrics["PROVENANCE"] == {"a": 1, "b": [1, 0]}


def test_combine_with_provenance_first_wins():
    t1 = {"a": 1, "b": [10, 20]}
    t2 = {"a": 99, "b": [30]}

    combined, metrics = combine(t1, t2, Resolver.FIRST, [DecisionMetric.PROVENANCE])
    assert combined == {"a": 1, "b": [10, 20]}
    assert metrics["PROVENANCE"] == {"a": 0, "b": [0, 0]}


def test_combine_with_audit_metric():
    t1 = {"a": 1, "b": 2}
    t2 = {"a": 99, "b": 2}  # conflict on 'a', clean on 'b'

    combined, metrics = combine(t1, t2, Resolver.LAST, [DecisionMetric.AUDIT])
    assert combined == {"a": 99, "b": 2}
    assert metrics["AUDIT"] == {"a": "conflict: `1` vs `99` -> `99`", "b": "clean"}


def test_combine_with_changelog_metric():
    t1 = {"a": 1, "b": 2}
    t2 = {"a": 99, "c": 3}

    combined, metrics = combine(t1, t2, Resolver.LAST, [DecisionMetric.CHANGELOG])
    assert combined == {"a": 99, "b": 2, "c": 3}
    assert metrics["CHANGELOG"] == {"a": "updated", "b": "unchanged", "c": "added"}


def test_combine_with_multiple_metrics_dict():
    t1 = {"a": 1, "b": 2}
    t2 = {"a": 99}

    combined, metrics = combine(
        t1, t2, Resolver.LAST,
        [DecisionMetric.PROVENANCE, DecisionMetric.AUDIT]
    )
    assert combined == {"a": 99, "b": 2}
    assert isinstance(metrics, dict)
    assert metrics["PROVENANCE"] == {"a": 1, "b": 0}
    assert metrics["AUDIT"] == {"a": "conflict: `1` vs `99` -> `99`", "b": "clean"}


def test_combine_with_custom_callback():
    t1 = {"a": 1}
    t2 = {"a": 2}

    def my_callback(t1, t2, res):
        return f"{t1}->{t2}"

    combined, metrics = combine(
        t1, t2, Resolver.LAST,
        [my_callback]
    )
    assert combined == {"a": 2}
    assert metrics["my_callback"] == {"a": "1->2"}


def test_combine_with_custom_callback_lambda():
    t1 = {"a": 1}
    t2 = {"a": 2}

    combined, metrics = combine(
        t1, t2, Resolver.LAST,
        [lambda t1, t2, res: f"{t1}->{t2}"]
    )
    assert combined == {"a": 2}
    assert metrics["<lambda>"] == {"a": "1->2"}


def test_combine_void_resolver():
    t1 = {"a": 1, "b": 2}
    t2 = {"a": 99}

    combined, metrics = combine(t1, t2, Resolver.VOID, [DecisionMetric.PROVENANCE])
    assert combined == {"b": 2}
    assert metrics["PROVENANCE"] == {"b": 0}


def test_combine_null_resolver():
    t1 = {"a": 1}
    t2 = {"a": 99}

    combined, metrics = combine(t1, t2, Resolver.NULL, [DecisionMetric.PROVENANCE])
    assert combined == {"a": None}
    assert metrics["PROVENANCE"] == {"a": None}


def test_combine_aggregative_resolver():
    t1 = {"a": 10}
    t2 = {"a": 20}

    combined, metrics = combine(t1, t2, NumericResolver.SUM, [DecisionMetric.PROVENANCE])
    assert combined == {"a": 30}
    assert metrics["PROVENANCE"] == {"a": None}


def test_combine_mismatched_structures():
    # conflict dict vs scalar resolved to dict (FIRST)
    t1 = {"a": {"b": 10}}
    t2 = {"a": 20}

    combined, metrics = combine(t1, t2, Resolver.FIRST, [DecisionMetric.PROVENANCE])
    assert combined == {"a": {"b": 10}}
    assert metrics["PROVENANCE"] == {"a": {"b": 0}}

    # conflict dict vs scalar resolved to scalar (LAST)
    combined, metrics = combine(t1, t2, Resolver.LAST, [DecisionMetric.PROVENANCE])
    assert combined == {"a": 20}
    assert metrics["PROVENANCE"] == {"a": 1}


def test_combine_none_metrics():
    t1 = {"a": 1}
    t2 = {"a": 2}
    combined = combine(t1, t2, Resolver.LAST, None)
    assert combined == {"a": 2}


def test_combine_custom_callable_op():
    t1 = {"a": 10}
    t2 = {"a": 20}
    combined, metrics = combine(
        t1, t2, lambda x, y: x + y, [DecisionMetric.PROVENANCE]
    )
    assert combined == {"a": 30}
    assert metrics["PROVENANCE"] == {"a": None}


def test_combine_resolved_container_t2():
    t1 = {"a": 10}
    t2 = {"a": {"b": 20}}
    combined, metrics = combine(t1, t2, Resolver.LAST, [DecisionMetric.PROVENANCE])
    assert combined == {"a": {"b": 20}}
    assert metrics["PROVENANCE"] == {"a": {"b": 1}}


def test_combine_resolved_container_new():
    t1 = {"a": 10}
    t2 = {"a": 20}

    # Resolver returns a brand new dict container
    def custom_resolver(x, y):
        return {"value": x + y}

    combined, metrics = combine(t1, t2, custom_resolver, [DecisionMetric.PROVENANCE])
    assert combined == {"a": {"value": 30}}
    assert metrics["PROVENANCE"] == {"a": {"value": None}}


def test_changelog_metric_unchanged_on_conflict():
    t1 = {"a": 1}
    t2 = {"a": 2}
    combined, metrics = combine(t1, t2, Resolver.FIRST, [DecisionMetric.CHANGELOG])
    assert combined == {"a": 1}
    assert metrics["CHANGELOG"] == {"a": "unchanged"}


class EqualButDistinct:
    def __init__(self, val):
        self.val = val

    def __eq__(self, other):
        return isinstance(other, EqualButDistinct) and self.val == other.val


def test_provenance_metric_equal_but_distinct_objects():
    t1 = {"a": EqualButDistinct(1)}
    t2 = {"a": EqualButDistinct(2)}

    # Custom resolver returning a new object equal to t1
    combined, metrics = combine(
        t1, t2, lambda x, y: EqualButDistinct(1), [DecisionMetric.PROVENANCE]
    )
    assert combined == {"a": EqualButDistinct(1)}
    assert metrics["PROVENANCE"] == {"a": 0}  # covers line 196

    # Custom resolver returning a new object equal to t2
    combined, metrics = combine(
        t1, t2, lambda x, y: EqualButDistinct(2), [DecisionMetric.PROVENANCE]
    )
    assert combined == {"a": EqualButDistinct(2)}
    assert metrics["PROVENANCE"] == {"a": 1}  # covers line 198


def test_calculate_metrics_list_with_missing():
    from mappingtools.typing import MISSING
    t1 = {"a": [1, 2]}
    t2 = {"a": [3]}
    combined, metrics = combine(t1, t2, Resolver.VOID, [DecisionMetric.PROVENANCE])
    assert combined == {"a": [MISSING, 2]}
    assert metrics["PROVENANCE"] == {"a": [MISSING, 0]}


def test_decision_metric_of_method():
    from mappingtools.typing import MISSING
    t1 = {"a": 1, "b": 2, "c": [10, 20]}
    t2 = {"a": 99, "b": 2, "c": [10]}
    combined, _ = combine(t1, t2, Resolver.VOID, [])

    # combined will be {"c": [MISSING, 20]}
    assert combined == {"c": [MISSING, 20]}

    prov_tree = DecisionMetric.PROVENANCE.of(combined, 1)
    audit_tree = DecisionMetric.AUDIT.of(combined, 1)
    changelog_tree = DecisionMetric.CHANGELOG.of(combined, 1)

    assert prov_tree == {"c": [MISSING, 1]}
    assert audit_tree == {"c": [MISSING, "clean"]}
    assert changelog_tree == {"c": [MISSING, "added"]}


def test_combine_with_conflict_count_metric():
    t1 = {"a": 1, "b": 2, "c": [10, 20]}
    t2 = {"a": 99, "b": 2, "c": [30]}

    combined, metrics = combine(t1, t2, Resolver.LAST, [DecisionMetric.CONFLICT_COUNT])
    assert combined == {"a": 99, "b": 2, "c": [30, 20]}
    # 'a' conflict (1 vs 99) -> 1
    # 'b' no conflict (2 vs 2) -> 0
    # c[0] conflict (10 vs 30) -> 1
    # c[1] non-overlapping (present only in t1) -> 0
    assert metrics["CONFLICT_COUNT"] == {"a": 1, "b": 0, "c": [1, 0]}


def test_conflict_count_metric_of_method():
    from mappingtools.typing import MISSING
    combined = {"a": 99, "b": 2, "c": [30, MISSING]}
    count_tree = DecisionMetric.CONFLICT_COUNT.of(combined, 1)
    assert count_tree == {"a": 0, "b": 0, "c": [0, MISSING]}


def test_combine_with_change_count_metric():
    t1 = {"a": 1, "b": 2, "c": [10, 20]}
    t2 = {"a": 99, "b": 2, "c": [30], "d": 4}

    # Case Resolver.LAST:
    # 'a': conflict (1 vs 99), resolved to 99 (updated) -> 1
    # 'b': no conflict (2 vs 2), resolved to 2 (unchanged) -> 0
    # 'c[0]': conflict (10 vs 30), resolved to 30 (updated) -> 1
    # 'c[1]': non-overlapping in t1 (20), resolved to 20 (unchanged) -> 0
    # 'd': non-overlapping in t2 (4), resolved to 4 (added) -> 1
    combined, metrics = combine(t1, t2, Resolver.LAST, [DecisionMetric.CHANGE_COUNT])
    assert combined == {"a": 99, "b": 2, "c": [30, 20], "d": 4}
    assert metrics["CHANGE_COUNT"] == {"a": 1, "b": 0, "c": [1, 0], "d": 1}

    # Case Resolver.FIRST:
    # 'a': conflict (1 vs 99), resolved to 1 (unchanged) -> 0
    # 'b': no conflict (2 vs 2), resolved to 2 (unchanged) -> 0
    # 'c[0]': conflict (10 vs 30), resolved to 10 (unchanged) -> 0
    # 'c[1]': non-overlapping in t1 (20), resolved to 20 (unchanged) -> 0
    # 'd': non-overlapping in t2 (4), resolved to 4 (added) -> 1
    combined, metrics = combine(t1, t2, Resolver.FIRST, [DecisionMetric.CHANGE_COUNT])
    assert combined == {"a": 1, "b": 2, "c": [10, 20], "d": 4}
    assert metrics["CHANGE_COUNT"] == {"a": 0, "b": 0, "c": [0, 0], "d": 1}


def test_change_count_metric_of_method():
    from mappingtools.typing import MISSING
    combined = {"a": 99, "b": 2, "c": [30, MISSING]}
    change_count_tree = DecisionMetric.CHANGE_COUNT.of(combined, 1)
    assert change_count_tree == {"a": 1, "b": 1, "c": [1, MISSING]}

    change_count_tree_side_0 = DecisionMetric.CHANGE_COUNT.of(combined, 0)
    assert change_count_tree_side_0 == {"a": 0, "b": 0, "c": [0, MISSING]}

