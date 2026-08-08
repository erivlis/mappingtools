"""CodSpeed benchmarks for `mappingtools.structures`."""

from mappingtools.structures import Dictifier, LazyDictifier, map_objects


def test_dictifier_method_proxy(benchmark, greeters, greeter_type):
    dictifier = map_objects(greeters, type_hint=greeter_type)
    result = benchmark(dictifier.greet, 'world')
    assert result


def test_dictifier_property_proxy(benchmark, greeters, greeter_type):
    dictifier = map_objects(greeters, type_hint=greeter_type)
    result = benchmark(lambda: dictifier.greeting_length)
    assert result


def test_dictifier_build(benchmark, greeters, greeter_type):
    result = benchmark(map_objects, greeters, type_hint=greeter_type)
    assert result


def test_dictifier_auto_build(benchmark, greeters):
    result = benchmark(Dictifier.auto, greeters)
    assert result


def test_lazy_dictifier_resolve(benchmark, greeters, greeter_type):
    def resolve():
        lazy = LazyDictifier(greeters, target_type=greeter_type)
        return dict(lazy.greet('world'))

    result = benchmark(resolve)
    assert result
