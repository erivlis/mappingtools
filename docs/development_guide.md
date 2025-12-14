---
icon: lucide/brain-circuit
---

# Development Guide & Philosophy

This document outlines the engineering philosophy and thought process behind `mappingtools`. It serves as a meta-guide
for how we approach problems, make decisions, and maintain quality.

## Core Philosophy: "Intuition-Led, Rigor-Backed"

We believe that good software architecture often starts with a "feeling"—an intuitive sense of symmetry, safety, or
simplicity. We trust these instincts but verify them with rigorous testing and analysis.

### 1. Trust the "Smell"

If a feature feels "off," "asymmetrical," or "too magical," stop immediately. Do not code through the doubt.

* **Action**: Pause development. Refactor the architecture until the feeling resolves.
* **Example**: We initially had separate `Dictifier` and `AutoDictifier` classes. This felt asymmetrical. We refactored them into a single `Dictifier` class with a `Dictifier.auto()` factory method.

### 2. Safety Over Magic

We prefer explicit, predictable behavior over implicit, "magical" behavior that might crash at runtime.

* **Action**: Isolate "magic" (like type inference) into separate classes or optional modes. Default to strictness.
* **Example**: `Dictifier` is strict by default. Auto-inference is only enabled via the explicit `Dictifier.auto()` factory.

### 3. The "Devil's Advocate" Testing

We don't just test that it works; we test that it fails correctly. We actively hunt for edge cases.

* **Action**: Write tests for empty collections, recursion loops, unresolvable type hints, and weird inheritance
  structures.
* **Example**: We added tests for generator methods to document their behavior, which led to the discovery of a subtle bug in our `async` detection logic.

### 4. Ergonomics First

Code is for humans. If the API is clunky, the implementation doesn't matter.

* **Action**: Design the "User Experience" of the library (imports, function names) before finalizing the
  implementation.
* **Example**: We added the `map_objects` factory and kept the `@dictify` decorator as a convenient alias for the more cohesive `Dictifier.of()` class method.

### 5. Prune Ruthlessly

Avoid the "Sunk Cost Fallacy." Just because we built it doesn't mean we keep it.

* **Action**: If a feature complicates the core value proposition without adding proportional value, sideline or delete
  it.
* **Example**: We built and then deleted the `AutoDictifier` class once we realized it was a "mode," not a "type."

## The Development Loop

When contributing to this project, follow this mental loop:

1. **Expand**: Brainstorm features (Async? Deep Proxying?).
2. **Critique**: Look for safety risks and API bloat.
3. **Refine**: Split classes, rename concepts, and simplify.
4. **Verify**: Write tests that try to break your new code.
5. **Reflect**: Does this align with the library's core mission?

## Architectural Patterns

*   **Mode vs. Type**: If you have two classes that differ only by a small behavior (like inference), consider merging them into one class with a mode flag or factory method.
*   **Factory Method Pattern**: If a decorator creates a specialized subclass, consider moving that logic into a `classmethod` on the base class (e.g., `Dictifier.of()`). It improves cohesion.

## Coding Standards

### Code Organization
*   **Regions**: Use `# region Region Name` and `# endregion` comments to group related functions or classes within a file. This improves navigability in large files.

### Testing
*   **AAA Pattern**: Structure tests using the **Arrange-Act-Assert** pattern. Use comments to explicitly delimit these sections.
    ```python
    def test_example():
        # Arrange
        data = {...}
        
        # Act
        result = process(data)
        
        # Assert
        assert result == expected
    ```

## Collaborating with AI

*   **The Meta-Cognitive Loop**: For AI agents, explicitly asking for "Thought Traces," "Design Reviews," or "SWOT Analyses" yields better results than just asking for code.
*   **Trust the Instinct**: When you feel "asymmetry" or a "code smell," communicate that feeling to the AI. It's a valuable signal that can trigger a productive refactoring path.

---
*This philosophy was distilled from the development session of the `structures` namespace.*
