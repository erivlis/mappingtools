"""
Recipe 03: Configuration Management (Monoids & Reduce)

This recipe demonstrates how to load multiple configuration layers
(e.g., default.json -> dev.json -> local.json) and cleanly merge them
into a single, unified state object.

Instead of writing a custom `ConfigurationManager` class, we use the `merge`
functional primitive combined with Python's built-in `functools.reduce`
to fold an iterable of dictionaries into one.
"""

import json
from functools import reduce

from mappingtools.operators import merge


def main():
    # 1. Define our "files" or "layers" of configuration.
    # In a real app, these would be loaded from disk or an API via `json.load`.
    default_config = {
        "logging": {"level": "INFO", "file": "/var/log/app.log"},
        "database": {"host": "localhost", "port": 5432},
        "plugins": ["auth", "cors"]
    }

    env_config = {
        "logging": {"level": "DEBUG"},  # Overwrite level, keep file
        "database": {"host": "db.production.local"},
        "plugins": ["metrics"]  # Append to list (Free Monoid)
    }

    user_overrides = {
        "theme": "dark",  # Add a new top-level key
        "database": {"pool_size": 10}  # Add a new nested key
    }

    # 2. Create a sequence of the loaded configurations in priority order
    layers = [default_config, env_config, user_overrides]

    # 3. Reduce the sequence using the `merge` Monoid.
    # This evaluates `merge(merge(default, env), user)`.
    # `MISSING` handles identity logic if any layer is empty.
    final_config = reduce(merge, layers)

    print("--- Final Merged Configuration ---")
    print(json.dumps(final_config, indent=2))


def test_main():
    main()


if __name__ == "__main__":
    main()
