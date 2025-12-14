---
icon: lucide/file-code
---

# Design Decisions

This document records the architectural decisions made during the development of `mappingtools`. It explains the "why"
behind the code.

## Core Project Philosophy

Based on the original structure of the library, we can infer several core design principles that guide the project.

### 1. Namespace as Intent

**Decision:** The library is organized into distinct namespaces: `collectors`, `operators`, `structures`, and
`transformers`.

* **Reasoning:** This is a strong architectural choice that separates concerns based on the *intent* of the operation.
    * `collectors`: For stateful aggregation of data.
    * `operators`: For stateless transformations of mappings (e.g., `inverse`, `flatten`).
    * `structures`: For advanced, dictionary-like data containers.
    * `transformers`: For reshaping the *content* of an object (e.g., `simplify`, `stringify`).

### 2. Functions Over Classes for Stateless Operations

**Decision:** The `operators` and `transformers` namespaces are composed almost entirely of pure functions.

* **Reasoning:** This reflects a functional programming influence. By avoiding classes for stateless operations, the
  code becomes more predictable, easier to test, and less prone to side effects. Classes (like `MappingCollector` or
  `MeteredDict`) are reserved for when managing state is the primary purpose of the object.

### 3. Immutability by Default

**Decision:** Core operators like `inverse`, `flatten`, `keep`, and `remove` return new dictionaries rather than
modifying their inputs.

* **Reasoning:** This prevents unexpected side effects. Users can trust that passing a dictionary to a `mappingtools`
  function will not alter the original data structure, which is crucial for building reliable data pipelines.

### 4. High Standard of Code Quality

**Decision:** The original codebase was fully typed, documented, and tested.

* **Reasoning:** This indicates a commitment to creating a maintainable, production-ready library. The high test
  coverage and clear docstrings serve as a foundation for future development.

---

## Namespace-Specific Decisions

### `collectors`

* **Decision:** Use classes (`MappingCollector`, `MeteredDict`) to manage stateful data aggregation.
* **Reasoning:** The primary purpose of this namespace is to collect data over time or track changes. This is an
  inherently stateful problem, making classes the natural choice over functions.
* **Specific Example (`MappingCollector`):** The decision to support multiple collection modes (`ALL`, `COUNT`,
  `DISTINCT`, etc.) within a single class allows for a unified interface for different aggregation strategies. This
  avoids a proliferation of small, specific collector classes.
* **Specific Example (`MeteredDict`):** This class wraps a dictionary to track access patterns. The decision to
  implement `MutableMapping` ensures it can be used as a drop-in replacement for a standard `dict` in most contexts,
  while adding the "metering" capability transparently.

### `operators`

* **Decision:** Provide pure, stateless functions that operate on mappings.
* **Reasoning:** Functions like `inverse` or `flatten` are mathematical transformations. They take an input and produce
  an output without side effects. Using pure functions makes them easy to reason about, test, and compose into larger
  data pipelines.
* **Specific Example (`inverse`):** The decision to handle duplicate values by creating sets (e.g., `{v: {k1, k2}}`)
  rather than overwriting ensures that the inversion process is lossless. This prioritizes data integrity over
  simplicity.
* **Specific Example (`stream`):** The inclusion of generator-based functions indicates a focus on memory efficiency for
  large datasets, allowing for lazy processing pipelines.

### `transformers`

* **Decision:** Provide pure functions that recursively process complex, nested objects.
* **Reasoning:** Similar to `operators`, these are stateless transformations. The key distinction is that they operate
  on the *content* and *shape* of objects (e.g., `simplify`, `stringify`), often involving recursion to handle nested
  data structures like lists and other dictionaries.
* **Specific Example (`simplify`):** The decision to recursively convert objects (like dataclasses or custom classes)
  into standard dictionaries allows for easy serialization (e.g., to JSON). This bridges the gap between Python's rich
  object model and external data formats.
* **Specific Example (`listify`):** This function transforms nested structures into a uniform list of key-value pairs.
  This decision supports use cases where a flat, list-based representation is required (e.g., for certain UI components
  or data exports).

### `structures`

* **Decision:** Create a new category for advanced, specialized data structures.
* **Reasoning:** This namespace is for classes that extend the capabilities of standard Python data structures (like
  `dict` or `list`) with significant new behaviors. While the initial focus is on proxying (`Dictifier`), the namespace
  is designed to hold any complex data container that doesn't fit the "stateless operator" or "simple collector"
  paradigms.

---

## The `structures` Namespace (Detailed)

This section details the specific decisions made during the implementation of the `Dictifier` family of classes.

### 1. Unified `Dictifier` with Strict and Auto Modes
**Decision:** We unified `Dictifier` and `AutoDictifier` into a single class with two modes.
*   **Context:** We initially had two separate classes.
*   **Reasoning:** "Auto-inference" is a behavior, not a fundamental type. A single, more powerful `Dictifier` class is a cleaner API. Strict mode is the default for safety, and auto-inference is explicitly enabled via the `Dictifier.auto()` factory method.

### 2. Intelligent Chaining (The Hybrid Approach)
**Decision:** Method proxies return a strict `Dictifier` if a return type hint is found, but fall back to a `Dictifier` in auto-inference mode if not.
*   **Context:** Python's dynamic nature makes it hard to know the return type of a proxied method at runtime without hints.
*   **Reasoning:** This hybrid approach offers the best of both worlds. Well-typed code gets full type safety deep into the chain. Untyped code (or built-ins) doesn't crash; it just degrades gracefully to inference-based chaining.

### 3. Deep Proxying via Type Hints
**Decision:** Field access (`users.address`) recursively wraps the result in a `Dictifier` *only* if the field has a class type hint.
*   **Context:** We wanted to support navigation like `users.address.city`.
*   **Reasoning:** Recursively wrapping everything is slow and confusing (wrapping primitives). Using type hints as the trigger makes the behavior predictable and aligns with the user's intent defined in their data model.

### 4. "Compile-Time" Optimization via Factory Method
**Decision:** The logic for pre-compiling proxies was moved from a standalone `@dictify` decorator into a `Dictifier.of()` class method.
*   **Context:** The generic `Dictifier` relies on `__getattr__`, which is slow. The decorator was a performance optimization.
*   **Reasoning:** Moving the optimization logic into the class itself improves cohesion (the class knows how to specialize itself). The `@dictify` decorator is kept as a convenient alias for `@Dictifier.of`.

### 5. LazyDictifier as a Separate Entity
**Decision:** `LazyDictifier` is a distinct class, not a mode of `Dictifier`.
*   **Context:** We considered merging them (`Dictifier(lazy=True)`).
*   **Reasoning:** The two have fundamentally different semantics. `Dictifier` is a **Mutable Snapshot** (you can add/remove items). `LazyDictifier` is an **Immutable View** (a computation pipeline). Merging them would create a confusing API with conflicting behaviors.

### 6. Async Support
**Decision:** `Dictifier` detects `async def` methods and returns an async proxy that uses `asyncio.gather`.
*   **Reasoning:** Modern Python relies heavily on async. Broadcasting an async call concurrently across a collection is a high-value feature that fits naturally with the "Batch Processing" mental model of the library.
