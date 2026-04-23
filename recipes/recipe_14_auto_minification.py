"""
Recipe 14: Dynamic Object Minification (minify vs simplify)

When exporting massive JSON datasets for front-end clients or network transmission,
long string keys ("customer_identifier_uuid", "transaction_timestamp_utc") waste bandwidth.

The `mappingtools` library provides `minify` to instantly solve this.
However, `minify` internally uses `strictify`. If your payload contains complex
non-standard objects (like Datetimes, Sets, or Dataclasses), `strictify` might choke
or fail to serialize them down to pure JSON primitives.

This recipe demonstrates how to combine `AutoMapper` manually with `strictify`
to achieve BOTH deep minification AND deep serialization simultaneously, ensuring
the output is 100% JSON-ready.
"""

from datetime import datetime, timezone

from mappingtools.collectors import AutoMapper
from mappingtools.transformers import strictify


def main():
    # 1. A complex business payload with bloated keys AND non-serializable objects (datetime)
    payload = {
        "customer_profile_information": {
            "customer_identifier_uuid": "user_99182",
            "primary_contact_email_address": "alice@example.com",
            "communication_preferences": {"email", "sms_marketing"} # This is a SET (Not JSON serializable!)
        },
        "transaction_history_records": [
            {
                "transaction_identifier_uuid": "tx_001",
                "transaction_timestamp_utc": datetime(2025, 10, 26, 12, 0, tzinfo=timezone.utc), # Datetime!
                "transaction_amount_usd_cents": 15000
            }
        ]
    }

    # 2. Create the Minifier Map
    # The AutoMapper automatically assigns unique strings 'A', 'B', 'C'...
    key_minifier = AutoMapper()

    # 3. Create a Key Transformer Function
    def minify_keys(key):
        # We only minify strings to protect integer indices or tuple keys.
        if isinstance(key, str):
            return key_minifier[key]
        return key

    # 4. Create a Value Transformer Function
    # strictify normally leaves non-standard primitives alone, which breaks json.dumps.
    # We define a custom value converter to handle datetime objects and sets!
    def serialize_values(value):
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, set):
            return list(value)
        return value

    # 5. Strictify the entire payload.
    # We use `strictify` directly and pass our custom key and value converters.
    minified_payload = strictify(payload, key_converter=minify_keys, value_converter=serialize_values)

    print("--- Original Payload Size (Estimated) ---")
    import json
    # json.dumps(payload) # This would crash because of datetime and set!
    print("Cannot easily dump original to JSON due to complex types (datetime, set).")

    print("\n--- Minified & Strictified Payload ---")
    minified_json = json.dumps(minified_payload, indent=2)
    print(f"Size: {len(json.dumps(minified_payload))} bytes")
    print(minified_json)

    print("\n--- De-Minification Legend ---")
    # Because AutoMapper is a dict, we can easily invert it to send to the client
    from mappingtools.operators import inverse
    legend = inverse(key_minifier)

    clean_legend = {k: v.pop() for k, v in legend.items()}
    print(json.dumps(clean_legend, indent=2))


def test_main():
    main()


if __name__ == "__main__":
    main()
