"""CodSpeed benchmarks for `mappingtools.operators`."""

import functools

import pytest

from mappingtools.aggregations import Aggregation
from mappingtools.operators import (
    KeyFormat,
    combine,
    distinct,
    flatten,
    inverse,
    merge,
    pivot,
    rekey,
    rename,
    reshape,
)
from mappingtools.resolvers import DecisionMetric, NumericResolver, Resolver


@pytest.mark.parametrize('key_format', list(KeyFormat), ids=lambda kf: kf.name)
def test_flatten_key_formats(benchmark, nested_tree, key_format):
    result = benchmark(flatten, nested_tree, key_format=key_format)
    assert result


def test_flatten_deep(benchmark, deep_tree):
    result = benchmark(flatten, deep_tree)
    assert result


def test_flatten_wide(benchmark, wide_tree):
    result = benchmark(flatten, wide_tree)
    assert result


def test_merge(benchmark, tree_pair):
    tree1, tree2 = tree_pair
    result = benchmark(merge, tree1, tree2)
    assert result


def test_merge_reduce(benchmark, tree_pair):
    trees = [*tree_pair, tree_pair[0], tree_pair[1]]
    result = benchmark(functools.reduce, merge, trees)
    assert result


def test_combine_last(benchmark, tree_pair):
    tree1, tree2 = tree_pair
    result = benchmark(combine, tree1, tree2, Resolver.LAST)
    assert result


def test_combine_numeric(benchmark, tree_pair):
    tree1, tree2 = tree_pair
    result = benchmark(combine, tree1, tree2, NumericResolver.MAX)
    assert result


def test_combine_with_decision_metrics(benchmark, tree_pair):
    tree1, tree2 = tree_pair
    result, metrics = benchmark(
        combine,
        tree1,
        tree2,
        Resolver.LAST,
        [DecisionMetric.CHANGE_COUNT, DecisionMetric.PROVENANCE],
    )
    assert result
    assert metrics


def test_distinct(benchmark, mappings):
    result = benchmark(lambda: list(distinct('a', *mappings)))
    assert result


def test_inverse(benchmark, set_mapping):
    result = benchmark(inverse, set_mapping)
    assert result


@pytest.mark.parametrize(
    'aggregation',
    [Aggregation.LAST, Aggregation.ALL, Aggregation.SUM, Aggregation.COUNT],
    ids=lambda a: a.name,
)
def test_pivot(benchmark, records, aggregation):
    result = benchmark(
        pivot,
        records,
        index='region',
        columns='product',
        values='units',
        aggregation=aggregation,
    )
    assert result


def test_reshape_three_levels(benchmark, records):
    result = benchmark(reshape, records, ['region', 'channel', 'product'], 'amount', Aggregation.SUM)
    assert result


def test_rekey(benchmark, wide_tree):
    result = benchmark(rekey, wide_tree, lambda k, v: v['value'] % 97)
    assert result


def test_rename_with_mapping(benchmark, wide_tree):
    mapper = {f'key_{i}': f'renamed_{i % 128}' for i in range(1000)}
    result = benchmark(rename, wide_tree, mapper, aggregation=Aggregation.ALL)
    assert result
