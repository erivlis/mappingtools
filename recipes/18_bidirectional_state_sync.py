"""
Recipe 18: Bi-directional State Sync (inverse + rekey)

In modern frontend-backend synchronizations (like React/Vue communicating with a Python API),
the frontend might use camelCase keys (`userId`, `createdAt`) while the Python backend
strictly uses snake_case (`user_id`, `created_at`).

This recipe demonstrates how to define a single source of truth mapping and then use
`inverse` to effortlessly translate payloads back and forth between the two systems.
"""

from mappingtools.operators import inverse, rekey


def main():
    # 1. The Single Source of Truth for our Field Mappings
    # (Python Backend Snake Case -> Frontend Camel Case)
    backend_to_frontend_map = {
        "user_id": "userId",
        "first_name": "firstName",
        "last_name": "lastName",
        "is_active": "isActive",
        "created_at": "createdAt"
    }

    # 2. Create the Reverse Mapping instantly
    # `inverse` automatically handles generating the (Frontend -> Backend) map.
    # Because `inverse` returns sets (to handle collisions), we extract the single item.
    frontend_to_backend_map = {
        k: next(iter(v)) for k, v in inverse(backend_to_frontend_map).items()
    }

    # 3. A Python Backend Record (Snake Case)
    python_db_record = {
        "user_id": 101,
        "first_name": "Alice",
        "last_name": "Smith",
        "is_active": True,
        "created_at": "2025-10-26T12:00:00Z"
    }

    print("--- Backend State (Snake Case) ---")
    import json
    print(json.dumps(python_db_record, indent=2))

    # 4. Serialize for the Frontend
    # We use `rekey` to translate the keys dynamically based on our map.
    def to_camel(key, val):
        return backend_to_frontend_map.get(key, key)

    frontend_payload = rekey(python_db_record, to_camel)

    print("\n--- Outbound Payload (Camel Case) ---")
    print(json.dumps(frontend_payload, indent=2))

    # 5. Assume the user updated their profile on the frontend
    frontend_update = {
        "userId": 101,
        "firstName": "Alice",
        "lastName": "Jones", # Changed last name
        "isActive": True
    }

    # 6. Deserialize back to the Backend
    def to_snake(key, val):
        return frontend_to_backend_map.get(key, key)

    backend_update = rekey(frontend_update, to_snake)

    print("\n--- Inbound Payload (Snake Case) ---")
    print(json.dumps(backend_update, indent=2))


if __name__ == "__main__":
    main()
