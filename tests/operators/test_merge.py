from functools import reduce

import pytest

from mappingtools.operators import merge
from mappingtools.optics import Lens
from mappingtools.typing import MISSING

trees_scenarios = [
    # Scalars
    (1, 2, 2),
    ("a", "b", "b"),
    (1, None, None),
    (None, 2, 2),

    # MISSING Identity (True Identity Element)
    (1, MISSING, 1),
    (MISSING, 2, 2),
    (None, MISSING, None),
    (MISSING, None, None),

    # Dictionaries
    ({"a": 1, "b": 2}, {"b": 3, "c": 4}, {"a": 1, "b": 3, "c": 4}),
    ({"x": {"y": 1}}, {"x": {"z": 2}}, {"x": {"y": 1, "z": 2}}),

    # Lists (Positional Zip)
    ([1, 2], [3], [3, 2]),
    ([1], [3, 4], [3, 4]),

    # Mixed List/Scalar (Free Monoid Fallback)
    ([1, 2], 3, [1, 2, 3]),  # List + Scalar -> Append
    (1, [2, 3], [1, 2, 3]),  # Scalar + List -> Prepend

    # Mixed Dict/Scalar (Scalar wins over Dict)
    ({"a": 1}, 2, 2),
    (1, {"a": 1}, {"a": 1}),
]


@pytest.mark.parametrize(("tree1", "tree2", "expected"), trees_scenarios)
def test_merge(tree1, tree2, expected):
    # Act
    merged = merge(tree1, tree2)

    # Assert
    assert merged == expected


def test_merge_reduce():
    # Arrange
    trees = [
        {"a": 1, "b": {"c": 2}},
        {"b": {"d": 3}},
        {"a": 10},
    ]

    # Act
    merged = reduce(merge, trees)

    # Assert
    assert merged == {"a": 10, "b": {"c": 2, "d": 3}}


def test_merge_with_lens():
    # Arrange
    system_state = {"system": {"config": {"retries": 3}}}
    new_config = {"timeout": 30}
    config_lens = Lens.path("system", "config")

    # Act
    new_state = config_lens.modify(
        system_state,
        lambda old: merge(old, new_config)
    )

    # Assert
    assert new_state == {"system": {"config": {"retries": 3, "timeout": 30}}}
    # Ensure original state wasn't mutated
    assert system_state == {"system": {"config": {"retries": 3}}}
