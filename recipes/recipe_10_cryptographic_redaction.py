"""
Recipe 10: Cryptographic Secret Redaction (flatten + Lenses + reduce)

In modern systems, logging deeply nested JSON payloads (like API requests)
is risky because they might contain hardcoded secrets, PII, or tokens.

This recipe demonstrates how to build an immutable "Redaction Pipeline".
We combine `flatten` to search the N-dimensional space for sensitive keys,
`hashlib` to cryptographically mask the values, and `Lens` + `reduce`
to immutably stamp the redacted values back into a safe copy of the tree.
"""

import hashlib
from functools import reduce

from mappingtools.operators import flatten
from mappingtools.optics import Lens


def hash_secret(value: str) -> str:
    """Cryptographically mask a value using SHA-256."""
    hashed = hashlib.sha256(str(value).encode('utf-8')).hexdigest()
    return f"[REDACTED: SHA256:{hashed[:8]}...]"

def main():
    # 1. A deeply nested payload from an API or Database
    raw_payload = {
        "request_id": "req_9981",
        "user": {
            "id": 1042,
            "profile": {
                "name": "Alice",
                "ssn": "000-11-2222" # Sensitive!
            },
            "credentials": {
                "api_key": "sk_live_abcdef1234567890", # Sensitive!
                "password_hash": "bcrypt_xyz",
                "oauth_token": {
                    "provider": "github",
                    "token": "gho_123456789" # Sensitive!
                }
            }
        }
    }

    # 2. Define our risk heuristics
    sensitive_keywords = {"api_key", "token", "ssn", "password"}

    # 3. Flatten the payload to easily search all N-dimensional paths
    flat_payload = flatten(raw_payload)

    # 4. Identify exactly which tuple paths point to sensitive data
    # Example path: ('user', 'credentials', 'oauth_token', 'token')
    sensitive_paths = [
        path for path in flat_payload
        if any(keyword in str(path[-1]).lower() for keyword in sensitive_keywords)
    ]

    print(f"--- Detected {len(sensitive_paths)} sensitive paths ---")
    for p in sensitive_paths:
        print(f" -> {'.'.join(map(str, p))}")

    # 5. Define a reducer function that takes the current state tree,
    # focuses on a specific path using a Lens, and hashes the value immutably.
    def apply_redaction(state_tree, path):
        # Create an Optic focused on the exact location of the secret
        target_lens = Lens.path(*path)
        # Modify the value immutably and return the new tree
        return target_lens.modify(state_tree, hash_secret)

    # 6. Fold the redactions over the payload
    # `reduce` pushes the `raw_payload` through every single Lens modification.
    safe_payload = reduce(apply_redaction, sensitive_paths, raw_payload)

    print("\n--- Safe Redacted Payload (Ready for Logging) ---")
    import json
    print(json.dumps(safe_payload, indent=2))

    print("\n--- Original Payload (Unchanged) ---")
    print(f"SSN remains untouched in memory: {raw_payload['user']['profile']['ssn']}")


def test_main():
    main()


if __name__ == "__main__":
    main()
