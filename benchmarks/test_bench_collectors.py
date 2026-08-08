"""CodSpeed benchmarks for `mappingtools.collectors`."""

import pytest

from mappingtools.aggregations import Aggregation
from mappingtools.collectors import (
    AutoMapper,
    CategoryCollector,
    CategoryCounter,
    DictOperation,
    MappingCollector,
    MeteredDict,
    nested_defaultdict,
)


@pytest.mark.parametrize(
    'aggregation',
    [Aggregation.ALL, Aggregation.COUNT, Aggregation.DISTINCT, Aggregation.LAST, Aggregation.SUM],
    ids=lambda a: a.name,
)
def test_mapping_collector_collect(benchmark, key_value_pairs, aggregation):
    def collect():
        collector = MappingCollector(aggregation=aggregation)
        collector.collect(key_value_pairs)
        return collector.mapping

    result = benchmark(collect)
    assert result


def test_mapping_collector_add(benchmark, key_value_pairs):
    def add_all():
        collector = MappingCollector(aggregation=Aggregation.ALL)
        for key, value in key_value_pairs:
            collector.add(key, value)
        return collector.mapping

    result = benchmark(add_all)
    assert result


def test_category_counter_dynamic_categories(benchmark, words):
    def count():
        counter = CategoryCounter()
        counter.collect(words, length=len, initial=lambda w: w[0], unique=lambda w: len(set(w)))
        return counter

    result = benchmark(count)
    assert result


def test_category_counter_constant_category(benchmark, words):
    def count():
        counter = CategoryCounter()
        counter.collect(words, source='bench')
        return counter

    result = benchmark(count)
    assert result


def test_category_collector(benchmark, words):
    def collect():
        collector = CategoryCollector(aggregation=Aggregation.DISTINCT)
        collector.collect(words, length=len, initial=lambda w: w[0])
        return collector

    result = benchmark(collect)
    assert result


def test_nested_defaultdict_fill(benchmark, records):
    def fill():
        tree = nested_defaultdict(2, list)
        for record in records:
            tree[record['region']][record['channel']][record['product']].append(record['units'])
        return tree

    result = benchmark(fill)
    assert result


def test_auto_mapper(benchmark, words):
    def map_all():
        mapper = AutoMapper()
        return [mapper[word] for word in words]

    result = benchmark(map_all)
    assert result


def test_metered_dict_workload(benchmark, key_value_pairs):
    operations = DictOperation.GET | DictOperation.SET | DictOperation.GET_DEFAULT

    def workload():
        metered = MeteredDict(operations=operations)
        for key, value in key_value_pairs:
            metered[key] = value
            metered.get(key)
        return metered.counts()

    result = benchmark(workload)
    assert result
