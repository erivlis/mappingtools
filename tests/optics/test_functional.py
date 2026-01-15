from mappingtools.optics.functional import patch, project
from mappingtools.optics.lens import Lens


def test_patch_basic():
    data = {'a': 1, 'b': 2}
    new_data = patch(data, {'a': 10})
    assert new_data == {'a': 10, 'b': 2}
    assert data == {'a': 1, 'b': 2}  # Immutability


def test_patch_nested():
    data = {'user': {'name': 'Alice', 'age': 30}}
    new_data = patch(data, {'user.name': 'Bob'})
    assert new_data['user']['name'] == 'Bob'
    assert data['user']['name'] == 'Alice'


def test_patch_with_lens():
    data = {'count': 1}
    lens = Lens.key('count')
    new_data = patch(data, {lens: 10})
    assert new_data['count'] == 10


def test_project_basic():
    data = {'user': {'name': 'Alice', 'version': 1}}
    result = project(data, {'username': 'user.name', 'v': 'user.version'})
    assert result == {'username': 'Alice', 'v': 1}


def test_project_with_lens():
    data = {'a': 1, 'b': 2}
    result = project(data, {'val_a': Lens.key('a'), 'val_b': 'b'})
    assert result == {'val_a': 1, 'val_b': 2}
