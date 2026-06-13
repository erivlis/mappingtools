"""
Recipe #31: Event Sanitization and Metadata Enrichment

Problem: A fraud-monitoring service receives nested partner events that include
class instances in multiple tree locations. The payload contains sensitive data
(tokens, emails) and must be normalized, sanitized, and annotated with process
metadata (`trace_id`, `updated_at`, `updated_by`) before persistence.

Solution:
1) Use `TraversalModeRegistry` + `strictify` to recursively traverse class
   instances and sanitize leaves in one pass.
2) Use `merge` to enrich every `metadata` mapping found in the resulting tree.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from mappingtools.operators import merge
from mappingtools.transformers import strictify
from mappingtools.traversal import TraversalMode, TraversalModeRegistry, traversal_mode


@dataclass
class Customer:
    name: str
    email: str
    auth_token: Any


@dataclass
class Order:
    order_id: str
    customer: Customer
    signature: bytes
    metadata: dict[str, Any]


class RedactableToken:
    """Iterable token wrapper that must stay atomic for sanitization."""

    def __init__(self, raw: str):
        self.raw = raw

    def __iter__(self):
        return iter(self.raw)


def _enrich_metadata_nodes(node: Any, metadata_patch: dict[str, Any]) -> Any:
    if isinstance(node, dict):
        updated = {}
        for key, value in node.items():
            if key == "metadata" and isinstance(value, dict):
                updated[key] = merge(value, metadata_patch)
            else:
                updated[key] = _enrich_metadata_nodes(value, metadata_patch)
        return updated
    if isinstance(node, list):
        return [_enrich_metadata_nodes(item, metadata_patch) for item in node]
    return node


def main():
    registry = TraversalModeRegistry()
    registry.register(bytes, TraversalMode.ITERABLE)
    registry.register(RedactableToken, TraversalMode.LEAF)

    @traversal_mode(TraversalMode.CLASS, registry=registry)
    class PartnerEnvelope:
        # Intentionally iterable for legacy adapter compatibility.
        def __init__(self, event_id: str, payload: dict[str, Any], metadata: dict[str, Any]):
            self.event_id = event_id
            self.payload = payload
            self.metadata = metadata

        def __iter__(self):
            return iter([self.event_id, self.payload, self.metadata])

    event_tree = {
        "primary": PartnerEnvelope(
            event_id=" evt-1001 ",
            payload={
                "order": Order(
                    order_id=" ord-9 ",
                    customer=Customer(
                        name="  Alice Doe ",
                        email="  ALICE@EXAMPLE.COM ",
                        auth_token=RedactableToken("tok_live_secret"),
                    ),
                    signature=b"\x0a\x0b",
                    metadata={"source": "partner-a"},
                )
            },
            metadata={"channel": "api"},
        ),
        "retry_queue": [
            {
                "snapshot": Order(
                    order_id=" ord-9 ",
                    customer=Customer(
                        name="  Alice Doe ",
                        email="  ALICE@EXAMPLE.COM ",
                        auth_token=RedactableToken("tok_live_secret"),
                    ),
                    signature=b"\x0a\x0b",
                    metadata={"attempt": 2},
                ),
                "metadata": {"worker": "retry-1"},
            }
        ],
    }

    def key_handler(key: Any) -> str:
        return str(key).strip().lower()

    def value_handler(value: Any) -> Any:
        if isinstance(value, RedactableToken):
            return "***REDACTED***"
        if isinstance(value, str):
            trimmed = value.strip()
            if "@" in trimmed:
                return trimmed.lower()
            return trimmed
        return value

    normalized = strictify(
        event_tree,
        key_handler=key_handler,
        value_handler=value_handler,
        traversal_registry=registry,
    )

    metadata_patch = {
        "trace_id": "trc-2026-000042",
        "updated_at": datetime(2026, 6, 13, 10, 30, tzinfo=timezone.utc).isoformat(),
        "updated_by": "pipeline:fim-enricher",
    }
    enriched = _enrich_metadata_nodes(normalized, metadata_patch)

    # Sanitization checks.
    primary_order = enriched["primary"]["payload"]["order"]
    retry_snapshot = enriched["retry_queue"][0]["snapshot"]

    assert primary_order["order_id"] == "ord-9"
    assert primary_order["customer"]["name"] == "Alice Doe"
    assert primary_order["customer"]["email"] == "alice@example.com"
    assert primary_order["customer"]["auth_token"] == "***REDACTED***"
    assert primary_order["signature"] == [10, 11]

    assert retry_snapshot["customer"]["email"] == "alice@example.com"
    assert retry_snapshot["customer"]["auth_token"] == "***REDACTED***"
    assert retry_snapshot["signature"] == [10, 11]

    # Metadata enrichment checks at multiple tree locations.
    assert enriched["primary"]["metadata"]["trace_id"] == "trc-2026-000042"
    assert enriched["primary"]["payload"]["order"]["metadata"]["updated_by"] == "pipeline:fim-enricher"
    assert enriched["retry_queue"][0]["metadata"]["updated_at"] == metadata_patch["updated_at"]
    assert enriched["retry_queue"][0]["snapshot"]["metadata"]["trace_id"] == "trc-2026-000042"

    print("Recipe 31 assertions passed.")


def test_main():
    main()


if __name__ == "__main__":
    main()
