# EP-001: Hybrid Recursive-Iterative Visitor for Robust Tree Traversal

**Status:** Draft
**Author:** Ariel
**Created:** 2026-05-10

## Abstract

This proposal details the design and implementation of a hybrid Visitor pattern for tree traversal within
`mappingtools`. The goal is to combine the performance and clarity of a recursive approach for common cases with the
robustness of an iterative, stack-based approach for deeply nested structures. This will prevent `RecursionError`
exceptions when processing untrusted or unusually deep data, without requiring external dependencies.

## Motivation

Several core functions in `mappingtools`, such as `merge` and `combine`, are implemented using recursion. This approach
is elegant, readable, and highly performant for the vast majority of use cases.

However, Python's lack of Tail-Call Optimization (TCO) imposes a hard limit on recursion depth (typically ~1,000 calls).
This creates a potential failure point when `mappingtools` is used to process data from uncontrolled sources (e.g.,
user-uploaded files, web crawls) where a malicious or malformed tree could easily exceed this depth, causing a
`RecursionError` and crashing the program.

The current workaround is to trust that the input data will not be excessively deep, which violates the principles of *
*Falsifiability** (assuming the happy path) and **Containment** (allowing uncontrolled input to crash the system).

## Rationale

To solve this, we need a mechanism that is both fast for the common case and safe for the worst case.

### Rejected Ideas

1. **Always Use Iterative Approach:** While safe, an iterative, stack-based approach is generally slower than a
   recursive one in Python for moderately deep trees due to interpreter overhead. Forcing all operations through this
   slower path violates the **Efficiency** principle.
2. **Pre-check Tree Depth:** To know the depth of a tree, one must traverse it. A recursive pre-check would face the
   same `RecursionError` it's trying to prevent. An iterative pre-check is redundant; at that point, one might as well
   perform the actual operation.

### Proposed Solution: The Hybrid Visitor Pattern

The most Pythonic and robust solution is a hybrid approach that embodies the "Easier to Ask for Forgiveness than
Permission" (EAFP) principle.

1. **Default to Fast:** Attempt the operation using a fast, recursive visitor.
2. **Catch and Fallback:** If, and only if, a `RecursionError` is caught, automatically switch to a robust, iterative
   visitor to complete the operation.

This provides the performance of recursion for >99% of cases while guaranteeing the program will not crash on the
exceptional cases.

Furthermore, implementing this as a **Visitor pattern** (inspired by `ast.NodeVisitor`) provides a clean, reusable, and
dependency-free architectural primitive for all current and future tree-traversal logic.

## Specification

### 1. Base Visitor Classes

We will implement two base visitor classes.

**`RecursiveTreeVisitor`:**
A simple, class-based visitor that uses standard recursion. It will provide a `visit(node)` method that dispatches to
`visit_<type_name>` methods and a `generic_visit` for default traversal.

**`IterativeTreeVisitor`:**
A robust, stack-based visitor. It will have a main `traverse(node)` method containing a `while` loop and an explicit
stack. Its `visit_<type_name>` methods will return child nodes to be added to the stack, rather than recursing.

### 2. `safe_merge` Implementation

The public-facing `merge` function will be refactored to use this hybrid strategy.

```python
# operators.py

def _recursive_merge(...):
    # Current fast implementation
    ...


def _iterative_merge(...):
    # New implementation using IterativeTreeVisitor
    ...


def merge(tree1, tree2):
    """
    Safely merges two trees, automatically falling back to an
    iterative approach for extremely deep structures.
    """
    try:
        return _recursive_merge(tree1, tree2)
    except RecursionError:
        # Log a warning that a fallback is occurring.
        print("WARNING: Deep recursion detected. Falling back to iterative merge.")
        return _iterative_merge(tree1, tree2)
```

The same pattern will be applied to `combine` and any other recursive operators.

## Backwards Compatibility

This change is fully backwards-compatible. The public API of `merge` and `combine` will not change. The behavior will be
identical, with the sole exception that they will now succeed on deeply nested trees instead of raising a
`RecursionError`. There may be a slight performance penalty in the rare event of a fallback, which is an acceptable
trade-off for robustness.

## Implementation Plan

1. Create a new module `mappingtools._visitors` to house the base visitor classes.
2. Implement `RecursiveTreeVisitor` and `IterativeTreeVisitor`.
3. Refactor `merge` and `combine` to use the hybrid `try/except` pattern, delegating to internal `_recursive` and
   `_iterative` implementations.
4. Add unit tests with deeply nested trees (>1000 levels) to verify that the fallback mechanism works as expected.
