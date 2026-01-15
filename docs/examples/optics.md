---
icon: lucide/square-dot
---

# Optics

!!! Abstract
    Optics provides functional, immutable tools for accessing and modifying deeply nested data structures. They allow you to
    separate the *shape* of your data from the logic that operates on it.

## Lens

A `Lens` is a composable, bidirectional accessor. It allows you to get and set values deep within a structure without
mutating the original object.

<!-- name: test_lens_basic -->

```python linenums="1"
from mappingtools.optics import Lens

data = {
    "users": [
        {
            "id": 1,
            "profile": {"name": "Ariel", "role": "Admin"}
        },
        {
            "id": 2,
            "profile": {"name": "Eran", "role": "User"}
        }
    ]
}

# Define a reusable lens for user names
# Path: "users" -> index 0 -> "profile" -> "name"
first_user_name = Lens.key("users") / 0 / "profile" / "name"

print(first_user_name.get(data))
# output: Ariel
```

### Immutable Modification

Lenses shine when you need to update a value deep in a structure without mutating the original object (Copy-on-Write).

<!-- name: test_lens_immutable_set -->

```python linenums="1"
from mappingtools.optics import Lens

data = {"user": {"profile": {"name": "Ariel"}}}
name_lens = Lens.key("user") / "profile" / "name"

# Update the name immutably
new_data = name_lens.set(data, "The Lion")

print(new_data["user"]["profile"]["name"])
# output: The Lion

print(data["user"]["profile"]["name"])
# output: Ariel
```

## patch

The `patch` function allows you to apply multiple changes at once using a dictionary of paths. This is useful for
applying configuration overrides or sanitizing data.

<!-- name: test_optics_patch -->

```python linenums="1"
from mappingtools.optics import patch, Lens

config = {
    "server": {
        "host": "localhost",
        "port": 8080,
        "debug": True
    },
    "db": {
        "name": "test"
    }
}

# Apply a patch
new_config = patch(config, {
    "server.host": "0.0.0.0",
    "server.debug": False,
    "db.name": "prod"
})

print(new_config)
# output: {'server': {'host': '0.0.0.0', 'port': 8080, 'debug': False}, 'db': {'name': 'prod'}}
```

## project

The `project` function allows you to reshape data into a flat or different structure based on a schema. This is useful
for creating API responses or UI views.

<!-- name: test_optics_project -->

```python linenums="1"
from mappingtools.optics import project, Lens

user = {
    "id": 123,
    "attributes": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
    },
    "meta": {
        "created_at": "2023-01-01",
        "active": True
    }
}

# Define a schema for the view
schema = {
    "uid": "id",
    "full_name": Lens.key("attributes") / "first_name",  # Can mix strings and Lenses
    "is_active": "meta.active"
}

view = project(user, schema)

print(view)
# output: {'uid': 123, 'full_name': 'John', 'is_active': True}
```
