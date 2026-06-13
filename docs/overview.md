---
icon: lucide/circle-ellipsis
---

# Overview

The **_MappingTools_** library is organized into several namespaces, each containing specific functionalities for
manipulating and transforming data structures.

## Library's Content

Below is a brief description of the main namespaces within the library:

=== ":lucide-square-sigma: Collectors"

    This namespace contains classes and functions for collecting and categorizing data items into mappings.
    
    | Class                  | Description                                                                                                              |
    |------------------------|--------------------------------------------------------------------------------------------------------------------------|
    | **AutoMapper**         | A Mapping-like class that automatically generates and assigns unique, minified strings values for any new keys accessed. |
    | **CategoryCollector**  | A generalized collector that aggregates data into categories (2D structure). Supports various aggregation modes.         |
    | **CategoryCounter**    | A specialized `CategoryCollector` for counting occurrences (Aggregation.COUNT).                                          |
    | **DictOperation**      | An enumeration of dictionary operations that can be tracked by `MeteredDict`.                                            |
    | **MappingCollector**   | Collects key-value pairs into an internal mapping based on different modes (ALL, COUNT, DISTINCT, FIRST, LAST).          |
    | **MappingCollectorMode** | An enumeration of modes for the `MappingCollector`.                                                                    |
    | **MeteredDict**        | A dictionary that tracks changes made to it.                                                                             |
    | **nested_defaultdict** | Creates a nested `defaultdict` with specified depth and factory.                                                         |

=== ":lucide-square-asterisk: Operators"

    This namespace provides functions that perform operations on mappings.

    | Function                             | Description                                                                                            |
    |--------------------------------------|--------------------------------------------------------------------------------------------------------|
    | **combine**                          | Generalizes `merge` by using a binary operator to resolve conflicts over deeply nested structures.     |
    | **distinct**                         | Yields distinct values for a specified key across multiple mappings.                                   |
    | **flatten**                          | Converts a nested mapping structure into a single-level dictionary by flattening the keys into tuples. |
    | **inverse**                          | Generates an inverse Mapping by swapping keys and values.                                              |
    | **merge**                            | Deeply merges two recursive tree structures.                                                           |
    | **pivot**                            | Reshapes a list of mappings into a nested dictionary based on index and column keys.                   |
    | **rekey**                            | Transforms keys based on a function of (key, value). Supports aggregation.                             |
    | **rename**                           | Renames keys based on a mapping or callable. Supports aggregation.                                     |
    | **reshape**                          | Reshapes a stream of mappings into a nested dictionary of arbitrary depth.                             |

=== ":lucide-square-dot: Optics"

    This namespace provides functional, immutable tools for accessing and modifying deeply nested data structures.

    | Class    | Description                                                                                                       |
    |----------|-------------------------------------------------------------------------------------------------------------------|
    | **Lens** | A functional optic for immutable access and modification of nested data structures. Supports composition via `/`. |
    
    | Function    | Description                                                                                               |
    |-------------|-----------------------------------------------------------------------------------------------------------|
    | **patch**   | Applies a set of changes to a data structure immutably using dot-separated paths or Lenses.               |
    | **project** | Projects a data structure into a new dictionary shape based on a schema of dot-separated paths or Lenses. |

=== ":lucide-square-code: Structures"

    This namespace provides advanced, dictionary-like data structures that act as proxies or containers for collections of objects.

    | Class             | Description                                                                                                                                                                                                                                                      |
    |-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | **Dictifier**     | A strict, type-safe container that proxies method calls and attribute access to a collection of objects. It requires an explicit type and enables deep proxying with type hints. For convenience, it offers an `auto()` factory method to enable type inference. |
    | **LazyDictifier** | A lazy version of `Dictifier` that defers execution until results are accessed. Ideal for large datasets or streaming pipelines where memory efficiency is critical.                                                                                             |

    | Function          | Description                                                                                                                                                                                                                                                      |
    |-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | **dictify**       | A class decorator that transforms a class definition into a specialized `Dictifier` collection, providing a declarative way to define object collections with optimized performance.                                                                             |
    | **map_objects**   | A factory function that provides a unified entry point for creating `Dictifier` or `LazyDictifier` instances based on the desired behavior (strict, auto, or lazy).                                                                                              |

=== ":lucide-square-function: Transformers"

    This namespace includes functions that reshape objects while maintaining the consistency of their structure.

    | Class           | Description                                                                                                             |
    |-----------------|-------------------------------------------------------------------------------------------------------------------------|
    | **Transformer** | A base class for creating reusable, composable data transformers with mode-based dispatch (`mapping/iterable/class/leaf`). |
    
    | Function      | Description                                                                                                                  |
    |---------------|------------------------------------------------------------------------------------------------------------------------------|
    | **listify**   | Transforms complex objects into a list of dictionaries with key/value pairs. Supports `traversal_registry`.               |
    | **minify**    | Shortens keys using a specified alphabet. Supports `traversal_registry`.                                                   |
    | **simplify**  | Converts objects to strictly structured dictionaries via `strictify`. Supports `traversal_registry`.                      |
    | **strictify** | Applies strict structural conversion using optional key/value converters. Supports `traversal_registry`.                  |
    | **stringify** | Converts an object into a string representation by recursively processing it by type. Supports `traversal_registry`.      |

=== ":lucide-square-star: Typing"

    This namespace provides custom type hints and utility functions for working with types within the library.
    
    | Type                 | Description                                                                                                                                                            |
    |----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
    | **Tree**             | A recursive type representing a tree structure where each node can be of a generic type `T`, a list of subtrees, or a dictionary mapping strings to subtrees.          |
    | **JsonScalar**       | Represents the basic scalar types found in JSON data (`None`, `bool`, `int`, `float`, `str`).                                                                          |
    | **JsonTree**         | A recursive type representing a JSON-like tree structure where each node can be a `JsonScalar`, a list of `JsonTree`s, or a dictionary mapping strings to `JsonTree`s. |
    | **EnhancedJsonTree** | A recursive type that extends `JsonTree` by allowing each node to also be of a generic type `T`, in addition to `JsonScalar`s, lists, or dictionaries.                 |
    | **MISSING**          | A sentinel object used to distinguish an explicit missing value from an actual `None` value, particularly in the `operators.merge` function.                           |
    | **Combine**          | A protocol for a callable that takes two objects of type `T` and combines them, returning `T`. Used by the `combine` operator.                                         |
    | **Handler**          | A protocol for a callable that takes an object of a generic type `T` and returns any value.                                                                            |

## Comparison with Other Libraries

`mappingtools` occupies a unique niche in the Python ecosystem.

Here is how it compares to other mapping and dictionary utility libraries.

### 1. Glom (`glom`)

- **Domain:** Declarative data restructuring and deep nested queries.
- **Comparison:**
    - **Glom** uses a custom query language/specification to query and restructure dicts.
    - **MappingTools** provides [Lens](guide/optics.md) for type-safe path optics and pure operators
      like [reshape](guide/operators.md) to pivot data shapes, maintaining native Python types and callbacks.
- **Verdict:** Use _Glom_ for complex query specs. Use _MappingTools_ for type-safe, composable path lenses and tensor-like
  reshaping.

### 2. Python Box (`python-box`)

- **Domain:** Transparent dictionary key-to-attribute access.
- **Comparison:**
    - **Box** wraps standard dicts to allow dot-notation access to keys (e.g., `box.key` instead of `box['key']`).
    - **MappingTools** provides [Dictifier](guide/structures), which acts as a functor/broadcaster to proxy method
      calls and attribute accesses to the *contained objects* (e.g., broadcasting `users.greet()` across a dict of
      `User` instances).
- **Verdict:** Use _Python Box_ for simple dot-notation dictionary lookups. Use _MappingTools_ for broadcasting method calls over
  object collections.

### 3. Toolz / Funcy (`toolz`, `funcy`)

- **Domain:** Functional utility functions for iterables and mappings.
- **Comparison:**
    - **Toolz/Funcy** provide flat, stateless helpers for dictionaries (e.g., `merge`, `valmap`).
    - **MappingTools** goes deeper with custom conflict-resolving [combine](guide/operators) operators, stateful
      collectors (like [MeteredDict](guide/collectors)), and structural transformers
      (see [transformers](guide/transformers)).
- **Verdict:** Use _Toolz_ for general functional programming primitives. Use _MappingTools_ for deep structural merging,
  modification, and telemetry collection.

!!! note "What about AlgebraX?"

    For advanced algebraic operations on mappings (such as Semirings, Sparse Matrix multiplication, and Graph
    pathfinding), please refer to the dedicated **[AlgebraX](https://github.com/erivlis/algebrax)** project,
    which was spun out from the early prototype stages of this library.

