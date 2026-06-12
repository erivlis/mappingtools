from collections.abc import Mapping

import pytest

from mappingtools.transformers import listify, minify, modify, simplify, stringify
from mappingtools.transformers.transformer import Transformer
from mappingtools.traversal import (
    TraversalMode,
    TraversalModeRegistry,
)
from mappingtools.visitors.operators import safe_merge


def _mapping_handler(obj, processor, *args, **kwargs):
    return 'mapping'


def _iterable_handler(obj, processor, *args, **kwargs):
    return 'iterable'


def _default_handler(obj):
    return 'leaf'


def _class_handler(obj, processor, *args, **kwargs):
    return 'class'


def test_traversal_registry_supports_decorator_registration():
    registry = TraversalModeRegistry()

    @registry.register(mode=TraversalMode.LEAF)
    class IterableLeaf:
        def __iter__(self):
            return iter([1, 2, 3])

    transformer = Transformer(
        iterable_handler=_iterable_handler,
        default_handler=_default_handler,
        traversal_registry=registry,
    )
    assert transformer(IterableLeaf()) == 'leaf'


def test_traversal_registry_can_force_iterable_class_to_class_mode():
    registry = TraversalModeRegistry()

    @registry.register(mode=TraversalMode.CLASS)
    class IterableClass:
        def __iter__(self):
            return iter([1, 2, 3])

    transformer = Transformer(
        iterable_handler=_iterable_handler,
        class_handler=_class_handler,
        default_handler=_default_handler,
        traversal_registry=registry,
    )
    assert transformer(IterableClass()) == 'class'


def test_traversal_registry_supports_imperative_registration():
    class MappingProxy:
        def __iter__(self):
            return iter(['a', 'b'])

        def items(self):
            return [('a', 1), ('b', 2)]

    registry = TraversalModeRegistry()
    registry.register(MappingProxy, TraversalMode.MAPPING)

    transformer = Transformer(
        mapping_handler=_mapping_handler,
        iterable_handler=_iterable_handler,
        default_handler=_default_handler,
        traversal_registry=registry,
    )
    assert transformer(MappingProxy()) == 'mapping'


def test_traversal_registry_can_force_mapping_to_leaf_in_transformer():
    class MappingLeaf(Mapping):
        def __init__(self):
            self._d = {'a': 1}

        def __iter__(self):
            return iter(self._d)

        def __len__(self):
            return len(self._d)

        def __getitem__(self, item):
            return self._d[item]

    registry = TraversalModeRegistry()
    registry.register(MappingLeaf, TraversalMode.LEAF)

    transformer = Transformer(
        mapping_handler=_mapping_handler,
        default_handler=_default_handler,
        traversal_registry=registry,
    )
    assert transformer(MappingLeaf()) == 'leaf'


def test_traversal_registry_resolves_using_mro_and_allows_child_override():
    class Parent:
        pass

    class Child(Parent):
        pass

    registry = TraversalModeRegistry()
    registry.register(Parent, TraversalMode.LEAF)
    assert TraversalMode.of(Child(), registry=registry) is TraversalMode.LEAF

    registry.register(Child, TraversalMode.CLASS)
    assert TraversalMode.of(Child(), registry=registry) is TraversalMode.CLASS


def test_traversal_registry_override_precedes_protocol_detection():
    class IterableNode:
        def __iter__(self):
            return iter([1, 2, 3])

    registry = TraversalModeRegistry()
    registry.register(IterableNode, TraversalMode.LEAF)

    mode = TraversalMode.of(IterableNode(), registry=registry)
    assert mode is TraversalMode.LEAF


def test_bytes_are_not_iterable_by_default():
    data = b'ab'
    transformer = Transformer(iterable_handler=_iterable_handler, default_handler=_default_handler)
    assert transformer(data) == 'leaf'


def test_bytes_are_iterable_only_with_explicit_registry_override():
    data = b'ab'
    registry = TraversalModeRegistry()
    registry.register(bytes, TraversalMode.ITERABLE)

    transformer = Transformer(
        iterable_handler=_iterable_handler,
        default_handler=_default_handler,
        traversal_registry=registry,
    )
    assert transformer(data) == 'iterable'


def test_registry_absent_keeps_baseline_transformer_behavior():
    transformer = Transformer(
        mapping_handler=_mapping_handler,
        iterable_handler=_iterable_handler,
        class_handler=_class_handler,
        default_handler=_default_handler,
    )

    assert transformer({'a': 1}) == 'mapping'
    assert transformer([1, 2]) == 'iterable'
    assert transformer(object()) == 'leaf'


def test_registry_absent_keeps_baseline_safe_merge_behavior():
    result = safe_merge({'a': [1, 2]}, {'a': [3]})
    assert result == {'a': [3, 2]}


def test_safe_merge_supports_registry_overrides():
    class LeafList(list):
        pass

    registry = TraversalModeRegistry()
    registry.register(LeafList, TraversalMode.LEAF)

    result = safe_merge(LeafList([1, 2]), [3], traversal_registry=registry)
    assert result == [1, 2, [3]]


def test_modify_accepts_traversal_registry():
    registry = TraversalModeRegistry()
    registry.register(bytes, TraversalMode.ITERABLE)
    assert modify(b'ab', traversal_registry=registry) == [97, 98]


def test_listify_accepts_traversal_registry():
    registry = TraversalModeRegistry()
    registry.register(bytes, TraversalMode.ITERABLE)
    assert listify(b'ab', traversal_registry=registry) == [97, 98]


def test_stringify_accepts_traversal_registry():
    registry = TraversalModeRegistry()
    registry.register(bytes, TraversalMode.ITERABLE)
    assert stringify(b'ab', traversal_registry=registry) == '[97, 98]'


def test_simplify_accepts_traversal_registry():
    registry = TraversalModeRegistry()
    registry.register(bytes, TraversalMode.ITERABLE)
    assert simplify(b'ab', traversal_registry=registry) == [97, 98]


def test_minify_accepts_traversal_registry():
    registry = TraversalModeRegistry()
    registry.register(bytes, TraversalMode.ITERABLE)
    assert minify(b'ab', traversal_registry=registry) == [97, 98]


def test_traversal_mode_of_detects_class_instance_without_registry():
    class PlainObject:
        def __init__(self):
            self.value = 1

    assert TraversalMode.of(PlainObject()) is TraversalMode.CLASS


def test_traversal_registry_register_requires_mode_for_decorator():
    registry = TraversalModeRegistry()
    with pytest.raises(ValueError, match=r"'mode' is required for decorator registration\."):
        registry.register()


def test_traversal_registry_register_requires_mode_for_type():
    registry = TraversalModeRegistry()
    with pytest.raises(ValueError, match=r"'mode' is required for type registration\."):
        registry.register(dict)


def test_traversal_registry_clear_removes_registered_modes():
    registry = TraversalModeRegistry()
    registry.register(dict, TraversalMode.LEAF)
    assert registry.resolve({}) is TraversalMode.LEAF
    registry.clear()
    assert registry.resolve({}) is None
