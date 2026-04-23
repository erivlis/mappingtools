"""
Recipe 01: Deep JSON Patching (Immutability & Optics)

This recipe demonstrates how to use the `Lens` optic and the `merge` function
to immutably update a deeply nested section of a large JSON-like dictionary.

Instead of writing brittle traversal logic (e.g., `data.get("a", {}).get("b", {})...`),
we compose a Lens to focus on the target, and then modify it using our pure `merge` monoid.
"""

from mappingtools.operators import merge
from mappingtools.optics import Lens


def main():
    # 1. Our large, deeply nested "State" or JSON payload
    app_state = {
        "server": {
            "host": "localhost",
            "port": 8080
        },
        "database": {
            "credentials": {
                "user": "admin",
                "password": "secret_password",
                "pool_size": 5
            },
            "tables": ["users", "sessions"]
        }
    }

    # 2. The "Patch" we want to apply to the database credentials
    db_patch = {
        "password": "new_secure_password",  # Overwrite existing
        "timeout_ms": 5000  # Add new field
    }

    # 3. Create an Optic (Lens) that focuses exactly on the credentials
    # This prevents us from having to manually traverse or mutate the outer layers.
    credentials_lens = Lens.path("database", "credentials")

    # 4. Apply the pure `merge` function OVER the focused node.
    # The `modify` method guarantees immutability; it returns a brand new state tree.
    new_app_state = credentials_lens.modify(
        app_state,
        lambda old_creds: merge(old_creds, db_patch)
    )

    print("--- Original State (Unchanged) ---")
    print(app_state["database"]["credentials"])

    print("\n--- New State (Patched) ---")
    print(new_app_state["database"]["credentials"])


def test_main():
    main()


if __name__ == "__main__":
    main()
