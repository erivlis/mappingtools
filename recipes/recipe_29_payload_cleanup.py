"""
Recipe #29: Cleaning Up API Payloads

Problem: You receive a complex, nested data structure from an external API and
need to clean it up before processing. This includes normalizing keys and trimming
whitespace from string values.

Solution: Use the `modify` transformer to apply multiple cleaning functions in a
single, declarative pass.
"""
import json

from mappingtools.transformers import modify


def main():
    # An example of a messy payload from an external source
    dirty_payload = {
        "  USER_ID  ": 123,
        "Profile": {
            "FirstName": "  John ",
            "LastName": "Doe  ",
            "Contact": {
                "Email": "  john.doe@example.com",
                "  PASSWORD  ": "  s3cr3t_p@ssw0rd!  ",
            },
        },
        "Roles": ["  Admin  ", "  User "],
    }

    # Define handlers for cleaning keys and values
    def key_handler(key):
        return key.strip().lower()

    def value_handler(value):
        if isinstance(value, str):
            return value.strip()
        return value

    # Apply the handlers in a single pass
    clean_payload = modify(
        dirty_payload,
        key_handler=key_handler,
        value_handler=value_handler,
    )

    print("--- Original Payload ---")
    print(json.dumps(dirty_payload, indent=2))
    print("\n--- Cleaned Payload (keys normalized, values trimmed) ---")
    print(json.dumps(clean_payload, indent=2))

    expected_payload = {
        "user_id": 123,
        "profile": {
            "firstname": "John",
            "lastname": "Doe",
            "contact": {
                "email": "john.doe@example.com",
                "password": "s3cr3t_p@ssw0rd!",
            },
        },
        "roles": ["Admin", "User"],
    }

    assert clean_payload == expected_payload

    print("\nAssertion successful: The payload was correctly cleaned.")


def test_main():
    main()


if __name__ == "__main__":
    main()
