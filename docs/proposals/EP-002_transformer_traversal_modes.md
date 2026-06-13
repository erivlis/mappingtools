# EP-002 Transformer Traversal Modes

## Backwards Compatibility

This proposal is backwards-compatible by default.

- If no registry entries are configured, behavior matches current classification.
- Existing users are unaffected unless they opt in.

Potential behavior changes occur only where explicit overrides are registered.

## Reference Implementation Plan

1. Add `TraversalMode` enum and `TraversalModeRegistry`. ✅
2. Add a shared classification function (`TraversalMode.of(...)`) that applies precedence rules. ✅
3. Refactor transformer and visitor dispatch logic to use shared classifier. ✅
4. Add tests: ✅
   - decorator registration
   - imperative registration
   - MRO inheritance behavior
   - precedence over protocol detection
   - registry-absent baseline compatibility
5. Add docs with migration and examples. ✅ (recipes 30, 31)

## Testing Strategy

Minimum test matrix:

- Class with `__iter__` forced to `CLASS` ✅
- Mapping-like proxy forced to `MAPPING` ✅
- Type forced to `LEAF` and verified non-recursive behavior ✅
- Parent/child class registration and override behavior ✅
- Registry absent → baseline behavior unchanged ✅
- Registry passed to `Transformer`, `safe_merge`, `safe_combine`, and transformer functions ✅

## Security and Reliability Considerations

- Explicit registry instances are required at all call sites; no hidden global registry exists.
- `clear()` is available for deterministic test teardown.
- Mutable registries shared across test boundaries will leak state — use isolated instances per test.

## Rejected Alternatives

1. **Hardcoded exclusion lists**  
   Rejected as brittle and ecosystem-specific.

2. **Protocol-only detection forever**  
   Rejected due to semantic ambiguity and inability to express intent.

3. **Single monolithic traversal mode without registry**  
   Rejected because it cannot address per-type exceptions cleanly.

4. **Global shared registry**  
   Rejected in favor of explicit instance injection at every call site.

## Open Questions

1. ~~Should the library expose a default global registry, or require explicit instance injection?~~  
   **Resolved:** Explicit injection. Every consumer (`Transformer`, `safe_merge`, `safe_combine`, transformer functions) accepts an optional `traversal_registry` parameter. No global registry is exposed.

2. Should registry resolution be cached for performance?  
   Currently unresolved. MRO walk occurs on every `resolve()` call. Caching by `type` would be straightforward but adds complexity. Deferred for benchmarking.

3. ~~Should `LEAF` bypass class handlers entirely, or route through default handler?~~  
   **Resolved:** `LEAF` routes to `leaf_handler` if set; falls through to `default_handler`, then returns the object unchanged. It does not bypass the default handler.

4. How should generator-like types be documented?  
   Generators are classified as `ITERABLE` by default (only `str`, `bytes`, and `bytearray` are excluded). They are consumed on the first traversal visit. This should be documented as a one-shot behavior — generators are not replayable after traversal.

## Rollout Plan

- Phase 1: Implement registry and classifier behind current defaults. ✅
- Phase 2: Integrate with `Transformer`. ✅
- Phase 3: Integrate with Visitors (`safe_merge`, `safe_combine`). ✅
- Phase 4: Document migration and provide practical recipes (30, 31). ✅
- Phase 5: Evaluate whether internal helpers (`_is_traversal_iterable`, `_is_traversal_mapping`, `_is_traversal_class_instance`) should be part of the public API or remain private. **Deferred.**
