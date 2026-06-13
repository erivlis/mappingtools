import dataclasses
from collections.abc import Mapping

import pytest

from mappingtools.transformers import listify, minify, modify, simplify, stringify
from mappingtools.transformers.transformer import Transformer
from mappingtools.traversal import (
    TraversalMode,
    TraversalModeRegistry,
    _is_traversal_class_instance,
    _is_traversal_iterable,
    _is_traversal_mapping,
    traversal_mode,
)


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

    @traversal_mode(TraversalMode.LEAF, registry=registry)
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

    @traversal_mode(TraversalMode.CLASS, registry=registry)
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


def test_is_traversal_iterable_and_bytes_handling():
    seq = [1, 2, 3]
    gen = (x for x in [1])
    s = "abc"
    b = b"abc"
    ba = bytearray(b"abc")

    assert _is_traversal_iterable(seq) is True
    assert _is_traversal_iterable(gen) is True
    assert _is_traversal_iterable(s) is False
    assert _is_traversal_iterable(b) is False
    assert _is_traversal_iterable(ba) is False


def test_is_traversal_mapping_detection():
    class MappingNode(Mapping):
        def __init__(self):
            self._data = {'k': 1}

        def __getitem__(self, key):
            return self._data[key]

        def __iter__(self):
            return iter(self._data)

        def __len__(self):
            return len(self._data)

    assert _is_traversal_mapping({'a': 1}) is True
    assert _is_traversal_mapping(MappingNode()) is True
    assert _is_traversal_mapping([1, 2, 3]) is False
    assert _is_traversal_mapping('abc') is False


def test_is_traversal_class_instance_dataclass_and_object():
    @dataclasses.dataclass
    class DC:
        x: int

    class C:
        def __init__(self):
            self.y = 1

    assert _is_traversal_class_instance(DC(1)) is True
    assert _is_traversal_class_instance(C()) is True
    # Dataclass classes have __dict__, so this stays True by current contract.
    assert _is_traversal_class_instance(DC) is True
    assert _is_traversal_class_instance(123) is False


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


def test_traversal_registry_register_requires_mode():
    registry = TraversalModeRegistry()
    with pytest.raises(ValueError, match=r"'mode' is required for type registration\."):
        registry.register()


def test_traversal_registry_register_requires_obj_type():
    registry = TraversalModeRegistry()
    with pytest.raises(ValueError, match=r"'obj_type' is required for type registration\."):
        registry.register(mode=TraversalMode.LEAF)


def test_traversal_registry_register_requires_mode_for_type():
    registry = TraversalModeRegistry()
    with pytest.raises(ValueError, match=r"'mode' is required for type registration\."):
        registry.register(dict)


def test_traversal_mode_decorator_rejects_function():
    registry = TraversalModeRegistry()

    def regular_func():
        return 1

    with pytest.raises(TypeError, match=r"accepts classes/types only"):
        traversal_mode(TraversalMode.LEAF, registry=registry)(regular_func)


def test_traversal_mode_decorator_rejects_async_function():
    registry = TraversalModeRegistry()

    async def async_func():
        return 1

    with pytest.raises(TypeError, match=r"accepts classes/types only"):
        traversal_mode(TraversalMode.LEAF, registry=registry)(async_func)


def test_traversal_mode_decorator_rejects_generator_function():
    registry = TraversalModeRegistry()

    def generator_func():
        yield 1

    with pytest.raises(TypeError, match=r"accepts classes/types only"):
        traversal_mode(TraversalMode.LEAF, registry=registry)(generator_func)


def test_traversal_mode_requires_mode():
    registry = TraversalModeRegistry()
    with pytest.raises(ValueError, match=r"'mode' is required for traversal_mode registration\."):
        traversal_mode(None, registry=registry)  # type: ignore[arg-type]


def test_traversal_registry_clear_removes_registered_modes():
    registry = TraversalModeRegistry()
    registry.register(dict, TraversalMode.LEAF)
    assert registry.resolve({}) is TraversalMode.LEAF
    registry.clear()
    assert registry.resolve({}) is None


def test_traversal_mode_of_detects_slots_class_instance_without_registry():
    class SlotObject:
        __slots__ = ('value',)
        def __init__(self):
            self.value = 1

    assert TraversalMode.of(SlotObject()) is TraversalMode.CLASS


def test_traversal_registry_thread_safety_concurrent_access():
    import threading
    import time

    registry = TraversalModeRegistry()
    classes = [type(f"Class_{i}", (), {}) for i in range(100)]

    stop_event = threading.Event()

    def writer():
        i = 0
        while not stop_event.is_set():
            cls = classes[i % len(classes)]
            if i % 2 == 0:
                registry.register(cls, TraversalMode.LEAF)
            else:
                registry.clear()
            i += 1
            time.sleep(0.001)

    def reader():
        while not stop_event.is_set():
            for cls in classes:
                registry.resolve(cls)

    threads = []
    for _ in range(2):
        threads.append(threading.Thread(target=writer))
    for _ in range(4):
        threads.append(threading.Thread(target=reader))

    for t in threads:
        t.start()

    time.sleep(0.1)
    stop_event.set()

    for t in threads:
        t.join()


def test_traversal_registry_double_checked_lock_branch_coverage():
    registry = TraversalModeRegistry()

    class DictWithRace(dict):
        def __init__(self):
            super().__init__()
            self.first_check = True

        def __contains__(self, item):
            contained = super().__contains__(item)
            if not contained and self.first_check:
                self.first_check = False
                self[item] = TraversalMode.LEAF
            return contained

    registry._cache = DictWithRace()

    # This will hit the first check (false), populate the cache in contains,
    # enter the lock, hit the second check (true), and return from the second check.
    res = registry.resolve(int)
    assert res is TraversalMode.LEAF

