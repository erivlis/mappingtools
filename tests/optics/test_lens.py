import pytest

from mappingtools.optics.lens import Lens


def test_key_lens():
    # Arrange
    data = {'a': 1, 'b': 2}
    lens = Lens.key('a')

    # Act & Assert (Get)
    assert lens.get(data) == 1

    # Act (Set)
    new_data = lens.set(data, 10)

    # Assert (Set)
    assert new_data == {'a': 10, 'b': 2}
    assert data == {'a': 1, 'b': 2}  # Original is unchanged


def test_index_lens():
    # Arrange
    data = [10, 20, 30]
    lens = Lens.index(1)

    # Act & Assert (Get)
    assert lens.get(data) == 20

    # Act (Set)
    new_data = lens.set(data, 99)

    # Assert (Set)
    assert new_data == [10, 99, 30]
    assert data == [10, 20, 30]  # Original is unchanged


def test_attr_lens():
    # Arrange
    class User:
        def __init__(self, name, age):
            self.name = name
            self.age = age

    user = User(name='Alice', age=30)
    lens = Lens.attr('name')

    # Act & Assert (Get)
    assert lens.get(user) == 'Alice'

    # Act (Set)
    new_user = lens.set(user, 'Bob')

    # Assert (Set)
    assert new_user.name == 'Bob'
    assert user.name == 'Alice'  # Original is unchanged!

    # Lens.attr is immutable (uses copy.copy)
    assert new_user is not user


def test_item_lens_smart():
    # Arrange (Dictionary)
    d = {'a': 1}
    lens = Lens.item('a')

    # Act & Assert (Dictionary)
    assert lens.set(d, 2) == {'a': 2}

    # Arrange (List)
    items = [1, 2]
    lens = Lens.item(0)

    # Act & Assert (List)
    assert lens.set(items, 9) == [9, 2]


def test_composition():
    # Arrange
    data = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
    # Lens: data["users"][0]["name"]
    lens = Lens.key('users') / Lens.index(0) / Lens.key('name')

    # Act & Assert (Get)
    assert lens.get(data) == 'Alice'

    # Act (Set)
    new_data = lens.set(data, 'Charlie')

    # Assert (Set)
    assert new_data['users'][0]['name'] == 'Charlie'
    assert data['users'][0]['name'] == 'Alice'  # Deep immutability preserved for dicts/lists


def test_composition_magic():
    # Arrange
    data = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
    # Magic: Mixing Lens objects with raw keys/indices
    lens = Lens.key('users') / 0 / 'name'

    # Act & Assert (Get)
    assert lens.get(data) == 'Alice'

    # Act (Set)
    new_data = lens.set(data, 'Charlie')

    # Assert (Set)
    assert new_data['users'][0]['name'] == 'Charlie'


def test_composition_magic_reverse():
    # Arrange
    data = {'users': [{'name': 'Alice'}]}
    # Magic: "users" / Lens...
    lens = 'users' / Lens.index(0) / 'name'

    # Act & Assert
    assert lens.get(data) == 'Alice'


def test_path_lens():
    # Arrange
    data = {'users': [{'name': 'Alice'}]}
    lens = Lens.path('users', 0, 'name')

    # Act & Assert
    assert lens.get(data) == 'Alice'


def test_lens_callable():
    # Arrange
    data = {'count': 1}
    lens = Lens.key('count')

    # Act & Assert
    # Lenses are callable (alias for get)
    assert lens(data) == 1


def test_modify():
    # Arrange
    data = {'count': 1}
    lens = Lens.key('count')

    # Act
    new_data = lens.modify(data, lambda x: x + 1)

    # Assert
    assert new_data['count'] == 2


def test_lens_path_empty_raises():
    # Act & Assert
    with pytest.raises(ValueError):
        Lens.path()


def test_set_uncopyable_object():
    # Arrange
    class Uncopyable:
        def __copy__(self):
            raise TypeError('Cannot copy')

    container = {'obj': Uncopyable()}
    lens = Lens.item('obj')

    # Act & Assert (Dict)
    # Should raise TypeError because Lens.item refuses to mutate uncopyable containers
    # Wait, Lens.item handles dicts/lists explicitly.
    # If container is a dict, it creates a new dict.
    # So it works even if the value is uncopyable.
    new_container = lens.set(container, 2)
    assert new_container['obj'] == 2

    # Arrange (Uncopyable Container)
    class UncopyableContainer:
        def __init__(self):
            self.val = 1

        def __copy__(self):
            raise TypeError('Cannot copy')

    container = UncopyableContainer()
    lens = Lens.attr('val')

    # Act & Assert (Uncopyable Container)
    # Lens.attr uses copy.copy.
    # If copy fails, it falls back to mutation?
    # Let's check implementation:
    # try: new_s = copy.copy(s) except TypeError: new_s = s
    # So it mutates in place if uncopyable.
    lens.set(container, 2)
    assert container.val == 2
