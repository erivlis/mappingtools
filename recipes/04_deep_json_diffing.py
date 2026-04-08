"""
Recipe 04: Deep JSON Diffing

This recipe demonstrates how to use the `flatten()` operator to collapse
deeply nested JSON structures into single-layer dictionaries with tuple paths as keys.

Once flattened, comparing two nested structures to find additions,
removals, or changes becomes a trivial set operation on their keys.
"""

from mappingtools.operators import flatten


def main():
    # 1. Original JSON payload (e.g., User Profile)
    original_profile = {
        "user": {
            "id": 101,
            "name": "Alice",
            "preferences": {
                "theme": "light",
                "notifications": {"email": True, "sms": False}
            }
        }
    }

    # 2. Updated JSON payload
    updated_profile = {
        "user": {
            "id": 101,
            "name": "Alice Smith",          # Changed
            "preferences": {
                "theme": "light",
                "notifications": {"email": True, "push": True} # Removed SMS, Added Push
            }
        }
    }

    # 3. Flatten both structures into 1D dictionaries
    # Keys become tuples: ('user', 'preferences', 'theme')
    flat_original = flatten(original_profile)
    flat_updated = flatten(updated_profile)

    # 4. Perform set operations on the keys to find the diff
    keys_original = set(flat_original.keys())
    keys_updated = set(flat_updated.keys())

    added_keys = keys_updated - keys_original
    removed_keys = keys_original - keys_updated
    common_keys = keys_original.intersection(keys_updated)

    changed_keys = {
        k for k in common_keys
        if flat_original[k] != flat_updated[k]
    }

    print("--- Deep JSON Diff ---")
    print(f"Added: {[(k, flat_updated[k]) for k in added_keys]}")
    print(f"Removed: {[(k, flat_original[k]) for k in removed_keys]}")
    print(f"Changed: {[(k, f'{flat_original[k]} -> {flat_updated[k]}') for k in changed_keys]}")


if __name__ == "__main__":
    main()
