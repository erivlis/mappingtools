# For AI Agents

This document provides meta-instructions and guidelines for AI agents interacting with this project and its maintainers.

## Core Interaction Protocols

### 1. The "Thought Trace"

When handling complex requests (architecture, debugging, refactoring), always provide a structured "Thought Trace" at
the end of your response. This makes your reasoning transparent and allows the user to correct your logic.

**Format:**

```
[Thought Trace]
User Request: "..."
├── PERCEPTION: Identify the core intent and context.
├── REASONING: Analyze constraints, trade-offs, and patterns.
├── PLANNING: Outline the steps for execution.
└── GENERATION: Execute the plan.
```

### 2. The "Stop and Reflect" Trigger

If a user request seems to introduce "asymmetry," "magic," or "bloat," do not blindly execute it. Stop and ask:

* "Is this the right architectural abstraction?"
* "Does this violate the Single Responsibility Principle?"
* "Is there a simpler way to achieve this (e.g., a mode flag instead of a subclass)?"

### 3. The "Context-Action-Constraint" Rule

When suggesting prompts or refactors, follow this structure for clarity:

1. **Context**: "I have a `Dictifier` class."
2. **Action**: "Add `__slots__`."
3. **Constraint**: "Watch out for recursion."

## Architectural Heuristics

### Mode vs. Type

If two classes differ only by a small behavior (e.g., strict vs. inferred typing), prefer merging them into a single
class with a **Mode Flag** or a **Factory Method** (e.g., `Dictifier.auto()`) rather than maintaining a class hierarchy.

### Factory Method for Specialization

If a decorator creates a specialized subclass, move that logic into a `classmethod` on the base class (e.g.,
`Dictifier.of()`). This improves cohesion and keeps the logic where it belongs.

### Explicit Over Implicit

* **Safety First**: Default to strict, type-safe behavior.
* **Opt-In Magic**: Make "magic" behavior (like type inference) explicitly opt-in via factories or flags.

## User Persona: The Architect

The primary maintainer values:

* **Symmetry**: API surfaces should feel balanced and consistent.
* **Roots**: Understanding the "why" and the first principles behind a decision.
* **Robustness**: Testing edge cases (empty collections, recursion, broken hints) is more important than happy-path
  speed.
* **Honesty**: Prefer direct technical pushback over polite compliance.
