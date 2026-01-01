import copy
from dataclasses import dataclass

import pytest

from mappingtools.optics.lens import Lens


def test_key_lens():
    data = {"a": 1, "b": 2}
    lens = Lens.key("a")

    assert lens.get(data) == 1
    new_data = lens.set(data, 10)
    assert new_data == {"a": 10, "b": 2}
    assert data == {"a": 1, "b": 2}  # Original is unchanged


def test_index_lens():
    data = [10, 20, 30]
    lens = Lens.index(1)

    assert lens.get(data) == 20
    new_data = lens.set(data, 99)
    assert new_data == [10, 99, 30]
    assert data == [10, 20, 30]  # Original is unchanged


def test_attr_lens():
    @dataclass
    class User:
        name: str
        age: int

    user = User(name="Ariel", age=4)
    lens = Lens.attr("name")

    assert lens.get(user) == "Ariel"

    # Lens.attr is immutable (uses copy.copy)
    new_user = lens.set(user, "Lion")

    assert new_user.name == "Lion"
    assert user.name == "Ariel"  # Original is unchanged!


def test_composition():
    data = {"users": [{"name": "Ariel"}, {"name": "Eran"}]}

    # Lens: data["users"][0]["name"]
    # Using / operator for composition (path-like)
    lens = Lens.key("users") / Lens.index(0) / Lens.key("name")

    assert lens.get(data) == "Ariel"

    new_data = lens.set(data, "The Lion")

    assert new_data["users"][0]["name"] == "The Lion"
    assert data["users"][0]["name"] == "Ariel"  # Deep immutability preserved for dicts/lists


def test_magic_composition():
    data = {"users": [{"name": "Ariel"}, {"name": "Eran"}]}

    # Magic: Mixing Lens objects with raw keys/indices
    lens = Lens.key("users") / 0 / "name"

    assert lens.get(data) == "Ariel"

    new_data = lens.set(data, "The Lion")

    assert new_data["users"][0]["name"] == "The Lion"
    assert data["users"][0]["name"] == "Ariel"


def test_reverse_magic_composition():
    data = {"users": [{"name": "Ariel"}]}

    # Magic: Starting with a raw string
    lens = "users" / Lens.index(0) / "name"

    assert lens.get(data) == "Ariel"


def test_modify():
    data = {"count": 1}
    lens = Lens.key("count")

    new_data = lens.modify(data, lambda x: x + 1)
    assert new_data["count"] == 2


def test_uncopyable_object_attr_fallback():
    class Uncopyable:
        def __init__(self, value):
            self.value = value

        def __copy__(self):
            raise TypeError("Cannot copy")

        def __deepcopy__(self, memo):
            raise TypeError("Cannot copy")

    obj = Uncopyable(1)
    lens = Lens.attr("value")

    # Should fallback to mutation
    new_obj = lens.set(obj, 2)

    assert new_obj is obj  # Same object
    assert new_obj.value == 2
    assert obj.value == 2  # Mutated


def test_uncopyable_object_item_raises():
    class UncopyableContainer:
        def __init__(self):
            self.data = {}

        def __getitem__(self, item):
            return self.data[item]

        def __setitem__(self, key, value):
            self.data[key] = value

        def __copy__(self):
            raise TypeError("Cannot copy")

    container = UncopyableContainer()
    container["a"] = 1

    lens = Lens.item("a")

    # Should raise TypeError because Lens.item refuses to mutate uncopyable containers
    with pytest.raises(TypeError, match="Cannot set item immutably"):
        lens.set(container, 2)


def test_copyable_custom_container_item():
    class CopyableContainer:
        def __init__(self):
            self.data = {}

        def __getitem__(self, item):
            return self.data[item]

        def __setitem__(self, key, value):
            self.data[key] = value

        def __copy__(self):
            new_obj = CopyableContainer()
            new_obj.data = self.data.copy()
            return new_obj

    container = CopyableContainer()
    container["a"] = 1

    lens = Lens.item("a")

    # Should use copy and return new object
    new_container = lens.set(container, 2)

    assert new_container is not container
    assert new_container["a"] == 2
    assert container["a"] == 1  # Original unchanged


def test_lens_path_empty_raises():
    with pytest.raises(ValueError, match="Path must have at least one segment"):
        Lens.path()


def test_lens_callable():
    data = {"a": 1}
    lens = Lens.key("a")
    assert lens(data) == 1
