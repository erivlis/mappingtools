"""
Recipe 12: Schema-Guided Payload Correction (flatten + Lenses + merge)

When APIs evolve, incoming JSON payloads often contain deprecated keys,
wrong data types, or missing required fields.

This recipe demonstrates how to build an "Auto-Corrector" pipeline.
We use a lightweight, evolving schema specification to guide the correction.
- `flatten` discovers all paths in the raw payload.
- `Lens` precisely targets and casts/corrects invalid data immutably.
- `merge` applies missing default structures.
"""

from functools import reduce

from mappingtools.operators import flatten, merge
from mappingtools.optics import Lens


def main():
    # 1. The Raw Payload (Legacy or malformed data from a client)
    raw_payload = {
        "user": {
            "id": "1042",               # Schema expects an integer!
            "first_name": "Alice",      # Schema evolved: deprecated, use 'given_name'
            "last_name": "Smith",       # Schema evolved: deprecated, use 'family_name'
        },
        "settings": {
            "theme": "dark"
            # Missing 'notifications' object entirely!
        }
    }

    # 2. The Evolving Schema Spec
    # Defines expected types, migrations (renames), and structural defaults.
    schema_spec = {
        "type_casts": {
            ("user", "id"): int,
            ("user", "age"): int
        },
        "migrations": {
            ("user", "first_name"): ("user", "given_name"),
            ("user", "last_name"): ("user", "family_name")
        },
        "defaults": {
            "settings": {
                "notifications": {"email": True, "sms": False}
            }
        }
    }

    print("--- 1. Original Raw Payload ---")
    import json
    print(json.dumps(raw_payload, indent=2))

    # --- Pipeline Step A: Type Casting & Value Correction ---
    # We flatten the payload to inspect what we actually have.
    flat_payload = flatten(raw_payload)

    # Identify which paths need type casting
    paths_to_cast = [
        path for path in flat_payload
        if path in schema_spec["type_casts"]
    ]

    def apply_cast(state, path):
        target_type = schema_spec["type_casts"][path]
        lens = Lens.path(*path)
        # Safely cast the value
        return lens.modify(state, lambda val: target_type(val))

    casted_payload = reduce(apply_cast, paths_to_cast, raw_payload)

    # --- Pipeline Step B: Structural Migrations (Renaming Keys) ---
    # To rename a nested key, we get the value from the old Lens,
    # set it on the new Lens, and (optionally) we could remove the old one.
    # For simplicity, we just copy the value to the new location.
    def apply_migration(state, old_path):
        new_path = schema_spec["migrations"][old_path]
        old_lens = Lens.path(*old_path)
        new_lens = Lens.path(*new_path)

        try:
            val = old_lens.get(state)
            return new_lens.set(state, val)
        except KeyError:
            return state # Old path wasn't in the payload, skip

    migrated_payload = reduce(apply_migration, schema_spec["migrations"].keys(), casted_payload)

    # Note: A real migration would also delete the old keys.
    # migrated_payload["user"].pop("first_name", None)
    # migrated_payload["user"].pop("last_name", None)

    # --- Pipeline Step C: Apply Structural Defaults ---
    # We use `merge` to stamp the payload ON TOP OF the defaults.
    # Remember: `merge(A, B)` means B overwrites A.
    # So we want `merge(defaults, migrated_payload)`.
    final_payload = merge(schema_spec["defaults"], migrated_payload)

    print("\n--- 2. Final Corrected & Migrated Payload ---")
    print(json.dumps(final_payload, indent=2))


if __name__ == "__main__":
    main()
