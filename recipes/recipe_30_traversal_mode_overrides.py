"""
Recipe #30: Traversal Mode Overrides

Problem: In a fraud-monitoring ingestion pipeline, partners send payloads that
mix nested dicts, binary signatures, and iterable domain wrappers. Blind
protocol detection can flatten or merge these fields incorrectly.

Solution: Use `TraversalModeRegistry` + `traversal_mode(...)` with two library
operations:
1) `modify` for normalization
2) `merge` for policy/state composition
"""
from mappingtools.operators import merge
from mappingtools.transformers import modify
from mappingtools.traversal import TraversalMode, TraversalModeRegistry, traversal_mode


def main():
    # Traversal contracts for this ingestion domain.
    registry = TraversalModeRegistry()
    registry.register(bytes, TraversalMode.ITERABLE)

    class TagsBag:
        """Domain wrapper over tags. Iterable, but semantically atomic."""

        def __init__(self, *tags: str):
            self.tags = list(tags)

        def __iter__(self):
            return iter(self.tags)

        def __repr__(self):
            return f"TagsBag({self.tags!r})"

    registry.register(TagsBag, TraversalMode.LEAF)

    @traversal_mode(TraversalMode.CLASS, registry=registry)
    class PartnerEventEnvelope:
        """
        Legacy partner model is iterable for batch tooling compatibility.
        In modify semantics we treat it as CLASS to avoid iterable expansion.
        """

        def __init__(self, event_id: str, payload: dict):
            self.event_id = event_id
            self.payload = payload

        def __iter__(self):
            return iter([self.event_id, self.payload])

    # Operation 1: modify(...) normalizes keys/values in incoming partner payload.
    raw_event = {
        " Event_ID ": " evt-001 ",
        "Payload": {
            "Amount": " 4200 ",
            "Signature": b"\x01\x02\x03",
            "Tags": TagsBag("pci", "vip"),
        },
    }

    def key_handler(key):
        return str(key).strip().lower()

    def value_handler(value):
        if isinstance(value, str):
            return value.strip()
        return value

    normalized_event = modify(
        raw_event,
        key_handler=key_handler,
        value_handler=value_handler,
        traversal_registry=registry,
    )
    # bytes -> iterable override turns signature bytes into integer list
    assert normalized_event["payload"]["signature"] == [1, 2, 3]
    # TagsBag remains atomic due to LEAF override
    assert isinstance(normalized_event["payload"]["tags"], TagsBag)
    assert normalized_event["event_id"] == "evt-001"

    # Operation 2: merge(...) composes base risk policy with incoming event state.
    # Note: merge is protocol-based and does not accept traversal_registry.
    base_state = {
        "risk": {"priority": "normal", "requires_review": False},
        "event": PartnerEventEnvelope("evt-000", {"amount": "100"}),
    }
    incoming_state = {
        "risk": {"priority": "high"},
        "event": PartnerEventEnvelope("evt-001", normalized_event),
    }
    merged_state = merge(base_state, incoming_state)

    assert merged_state["risk"]["priority"] == "high"
    assert merged_state["risk"]["requires_review"] is False
    assert merged_state["event"] is incoming_state["event"]
    assert merged_state["event"].event_id == "evt-001"

    print("Traversal mode recipe assertions passed for fraud-ingestion scenario.")


def test_main():
    main()


if __name__ == "__main__":
    main()
