# EP-003: Context-Aware Traversal for Transformers

**Status:** Draft  
**Author:** Antigravity  
**Created:** 2026-06-13

## Abstract

This proposal introduces a design for **Context-Aware Traversal** inside the `mappingtools` transformer pipeline. The
goal is to provide type-safe, performant, and multi-dimensional traversal context (such as parent keys, key lineages,
nesting depth, and parent reference graphs) to key and value handlers. This will eliminate the need for developers to
write custom recursive utility functions to target specific paths or fields within complex event trees.

## Motivation

In complex applications, object transformations are rarely uniform. Often, a transformation must be applied selectively
based on the structural context of the field, rather than just its type or value. Common scenarios include:

- **Event Sanitization**: Redacting all values named `auth_token` only when they are nested under
  `customer.auth_token` (avoiding false-positive redaction of unrelated fields sharing the same value or key).
- **Targeted Enrichment**: Injecting process metadata (e.g., `trace_id`) only into sub-dictionaries specifically keyed
  as `metadata` (as illustrated in Recipe 31).
- **Depth-Restricted Formatting**: Stringifying nested structures only up to a nesting depth of 3, leaving deeper
  elements unmodified.

Currently, `Transformer` dispatching and handler interfaces are context-unaware:

- Key handlers accept only the key: `key_handler(key)`
- Value/default handlers accept only the value: `value_handler(value)`

As a result, users wanting to apply context-sensitive rules must write custom recursive traversal helpers (violating *
*Consistency**), or manually track state inside stateful closures during execution (which violates **Safety** and is not
thread-safe).

## Proposed Design

To represent context, we propose introducing a `TraversalContext` value object that is passed to handlers.

### 1. The `TraversalContext` Structure

We define a read-only context descriptor:

```python
@dataclass(frozen=True)
class TraversalContext:
    key: Any | None
    """The immediate parent key or sequence index associated with the current node."""

    parent: Any | None
    """Reference to the immediate parent container object."""

    lineage: tuple[Any, ...]
    """The full path of keys/indices traversed from the root to the current node."""

    depth: int
    """The current nesting depth of the node (0 represents the root)."""
```

### 2. Context Propagation in `Transformer`

The core loop in `Transformer._transform` will maintain the current path lineage and nesting depth. To prevent
allocation overhead on every node when context is not required, the tracking should be optional or lazily initialized:

- **Option A (Signature Inspection)**: Eagerly analyze the signature of the registered handler (e.g., using
  `inspect.signature`). If the handler accepts a `context` argument, propagate context; otherwise, call it with a single
  argument.
- **Option B (Context Flag/Opt-in)**: Expose an explicit boolean parameter `enable_context` (or `context_mode=True`) on
  the `Transformer` and wrapper functions. When `False`, context is not tracked, preserving raw speed.

### 3. Integration with Optics (Lenses)

A key advantage of tracking lineage is the ability to unify **Transformers** and **Optics**. Since `Lens` compositions represent paths, the `TraversalContext` can expose a property to lazily generate a functional `Lens` pointing to the current node:

```python
class TraversalContext:
    # ...
    
    @property
    def lens(self) -> Lens:
        """Lazily construct a Lens focusing from the root to the current node."""
        from mappingtools.optics.lens import Lens
        if not self.lineage:
            return Lens(lambda s: s, lambda s, v: v)  # Identity
            
        l = Lens.item(self.lineage[0])
        for k in self.lineage[1:]:
            l = l / k
        return l
```

This makes it extremely easy to build validation, search, or side-effect tools that crawl a tree, collect lenses of targeted nodes, and return them so the caller can fetch or modify the root object later.

### 4. Usage Example

With context-aware handlers, event sanitization and metadata enrichment from Recipe 31 can be simplified to:

```python
def value_handler(value: Any, ctx: TraversalContext) -> Any:
    # 1. Target redaction at specific path
    if ctx.lineage == ("primary", "payload", "order", "customer", "auth_token"):
        return "***REDACTED***"

    # 2. Target enrichment by parent key name
    if ctx.key == "metadata" and isinstance(value, dict):
        return merge(value, metadata_patch)

    return value


normalized = strictify(
    event_tree,
    value_handler=value_handler,
    enable_context=True,
)
```


## Backwards Compatibility

This proposal is designed to be fully backwards-compatible:

- Default behavior: `enable_context=False`. Handlers receive single parameters (`key` or `value`) as before.
- If a custom handler does not support the context argument, it is called using its legacy signature.

## Testing Strategy

Minimum test matrix:

- **Path Lineage Match**: Assert that the `lineage` path tuple is correctly built for mapping keys and sequence indices.
- **Depth Assertion**: Assert that nested dictionary values have a matching `depth` integer.
- **Parent Reference Check**: Assert that the handler can inspect the `parent` container to make decisions based on
  sibling keys.
- **Opt-in Performance Benchmark**: Compare the performance of the transformer with `enable_context=True` vs
  `enable_context=False` to measure path allocation overhead.

## Security and Reliability Considerations

- **Thread-Safety**: The `TraversalContext` object is immutable (`frozen=True`) and context stacks are maintained on the
  call-frame or task-stack, making it thread-safe.
- **Reference Leaks**: Keeping a reference to `parent` could hold large trees in memory if the context objects
  themselves are cached or stored globally. Handlers must not persist `TraversalContext` instances outside the transform
  life-cycle.

## Rejected Alternatives

1. **Global Thread-Local Context Stack**  
   Rejected in favor of explicit context passing to keep handlers functional, predictable, and easily testable in
   isolation.

2. **Passing Raw Path List to Handlers**  
   Rejected because passing multiple individual parameters (e.g., `value_handler(value, key, parent, path)`) makes the
   handler signatures brittle and difficult to extend in the future. A single `TraversalContext` object allows adding
   attributes without breaking signatures.

## Open Questions

1. Should sequence indices (integers) be included in `lineage`, or only mapping/attribute keys?  
   *Current thought:* Yes, sequence indices are necessary to reconstruct the exact index-path (e.g.,
   `("retry_queue", 0, "snapshot")`).
2. Should class instance attribute names be tracked as strings in the `lineage`?  
   *Current thought:* Yes, class attributes behave like mapping keys during traversal and should be represented in the
   lineage.
3. How does this affect visitors?  
   *Current thought:* Visitors (`RecursiveTreeVisitor` / `IterativeTreeVisitor`) could also accept a `TraversalContext`,
   but that would require modifying the visitor stack loop. This should be addressed in a separate Phase.
