"""
Recipe 17: Data Governance & Role-Based Access Control (RBAC) (rename + Lens)

In large organizations, returning JSON data to an API client often requires
"shaping" the response based on the user's role (e.g., an Admin sees everything,
a standard User sees limited fields, an External client sees sanitized data).

This recipe combines native Python comprehensions (to strip internal metadata),
the `rename` operator (to map database columns to public API schemas),
and `Lens` optics (to mask/redact sensitive nested data) to construct
a flexible Data Governance pipeline.
"""

from mappingtools.operators import rename
from mappingtools.optics import Lens


def main():
    # 1. A simulated raw record loaded straight from a database query
    raw_user_record = {
        "db_internal_id": 9941,
        "uuid_str": "usr_abc123",
        "first_name": "Bob",
        "last_name": "Smith",
        "salary_tier": "T4",
        "created_at": "2024-01-01T12:00:00Z",
        "profile": {
            "email": "bob@corporate.internal",
            "phone": "555-0100"
        },
        "_sys_modified_by": "admin_joe" # Internal tracking metadata
    }

    # 2. Define our Governance Rules for an "External Client" API Response

    # A. Fields to completely strip out of the response
    internal_keys_to_strip = {"db_internal_id", "_sys_modified_by", "salary_tier"}

    # B. Fields to rename to match our public API schema
    public_api_schema_map = {
        "uuid_str": "id",
        "first_name": "givenName",
        "last_name": "familyName"
    }

    # C. Fields to redact/mask (Optics focus)
    phone_lens = Lens.path("profile", "phone")
    def mask_phone(phone_str: str) -> str:
        """Replace all but the last 4 digits with asterisks."""
        return "*" * (len(phone_str) - 4) + phone_str[-4:] if phone_str else ""


    # 3. Build the Data Shaping Pipeline
    print("--- 1. Raw Database Record ---")
    import json
    print(json.dumps(raw_user_record, indent=2))

    # Step A: Strip internal metadata.
    # Since `remove` is deprecated, we use a native dictionary comprehension.
    cleansed_record = {
        k: v for k, v in raw_user_record.items()
        if k not in internal_keys_to_strip
    }

    # Step B: Rename columns to the public schema
    # Keys not in the map remain untouched
    schema_compliant_record = rename(cleansed_record, public_api_schema_map)

    # Step C: Apply PII Masking immutably
    safe_public_response = phone_lens.modify(schema_compliant_record, mask_phone)

    print("\n--- 2. Shaped Public API Response ---")
    print(json.dumps(safe_public_response, indent=2))


def test_main():
    main()


if __name__ == "__main__":
    main()
