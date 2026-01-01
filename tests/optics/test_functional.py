from mappingtools.optics.functional import patch, project
from mappingtools.optics.lens import Lens


def test_patch_dict():
    data = {"user": {"name": "Ariel", "version": 1}}
    changes = {
        "user.name": "Lion",
        "user.version": 2
    }

    new_data = patch(data, changes)

    assert new_data["user"]["name"] == "Lion"
    assert new_data["user"]["version"] == 2
    assert data["user"]["name"] == "Ariel"  # Immutability check


def test_patch_list():
    data = {"users": ["Ariel", "Eran"]}
    changes = {
        "users.0": "Lion"
    }

    new_data = patch(data, changes)

    assert new_data["users"][0] == "Lion"
    assert data["users"][0] == "Ariel"


def test_patch_with_lens():
    data = {"count": 1}
    lens = Lens.key("count")

    new_data = patch(data, {lens: 10})

    assert new_data["count"] == 10


def test_project():
    data = {
        "user": {
            "profile": {
                "name": "Ariel",
                "id": 123,
                "email": "ariel@example.com"
            },
            "meta": {"active": True}
        }
    }

    schema = {
        "name": "user.profile.name",
        "uid": "user.profile.id",
        "is_active": "user.meta.active"
    }

    view = project(data, schema)

    assert view == {
        "name": "Ariel",
        "uid": 123,
        "is_active": True
    }


def test_project_with_lens():
    data = {"a": 1, "b": 2}
    schema = {
        "val_a": Lens.key("a")
    }

    view = project(data, schema)
    assert view == {"val_a": 1}
