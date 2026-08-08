"""CodSpeed benchmarks for `mappingtools.transformers`."""

from mappingtools.transformers import listify, minify, simplify, strictify, stringify


def test_stringify(benchmark, nested_tree):
    result = benchmark(stringify, nested_tree)
    assert result


def test_stringify_class_tree(benchmark, class_tree):
    result = benchmark(stringify, class_tree)
    assert result


def test_listify(benchmark, nested_tree):
    result = benchmark(listify, nested_tree)
    assert result


def test_listify_class_tree(benchmark, class_tree):
    result = benchmark(listify, class_tree)
    assert result


def test_simplify(benchmark, nested_tree):
    result = benchmark(simplify, nested_tree)
    assert result


def test_minify(benchmark, nested_tree):
    result = benchmark(minify, nested_tree)
    assert result


def test_strictify(benchmark, class_tree):
    result = benchmark(strictify, class_tree, key_handler=str)
    assert result
