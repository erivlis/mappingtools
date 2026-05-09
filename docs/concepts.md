---
icon: lucide/circle-star
---

# Core Concepts

`mappingtools` is a pragmatic utility library, but beneath the surface, it relies on a very specific, consistent
mathematical framework. Understanding this mental model will allow you to compose the library's primitives with
confidence.

## 1. The Substrate: The Recursive Tree

Before you can manipulate data, you must define its shape. In `mappingtools`, the bedrock data structure is the `Tree`.

If you look at the library's type hints (`typing.py`), you will see this definition:

```python
Tree: TypeAlias = T | list['Tree[T]'] | dict[str, 'Tree[T]']
```

In type theory, this is known as a **Recursive Sum Type** or an **Algebraic Data Type (ADT)**. Specifically, it models a
*Rose Tree*—a tree with an arbitrary number of branches per node.

This simple definition is profound because it mathematically describes **JSON**.
It states that any node in our data is exactly one of three things:

1. **A Leaf (`T`)**: A scalar value (string, integer, boolean).
2. **A Sequence (`list`)**: An ordered, unnamed list of subtrees.
3. **A Mapping (`dict`)**: A labeled, unordered set of subtrees.

Because the library restricts itself to operating *only* on this specific mathematical structure, we can guarantee that
operations like `combine` or `flatten` will recurse safely and predictably over any JSON-like payload.

---

## 2. The Mental Model of Operations

When you write data engineering pipelines or handle configurations, you are almost always doing one of three things to
these trees. We classify all operations in the library by how they flow over the data:

### Unary Operations: Transforming a Single Tree

When you need to mutate the shape, keys, or values of a single object, you are performing a **Unary Operation**. The
structure changes, but you are only dealing with one source of truth at a time.

**The Analogy:** Imagine walking through a single maze, changing the color of the walls as you go.

- **Tools to use:**
    - **`Transformer` class and operations (`minify`, `strictify`, `simplify`, etc.)**
      
        These lift a set of scalar rules ("make all datetimes into ISO strings") and apply them recursively across the entire tree.
  
    - **Optics (`Lens`):**
      
        For precise, surgical strikes on a specific, deeply nested node within a single tree, without mutating the
        original structure.

### Binary Operations: Fusing Two Trees

When you have two parallel structures (e.g., a default configuration and a user configuration) and you need to combine
them, you are performing a **Binary Operation**.

**The Analogy:** Imagine overlaying two identical mazes on top of each other. Where the walls overlap perfectly, there
is no issue. Where they differ, you have a **conflict** that must be resolved.

- **Tools to use:**
    - **`combine`:**
    
        This is the engine of binary combination. You provide it with two trees and an `op` (a `Resolver` rule
        for handling conflicts at the leaf level, like `SUM`, `FIRST`, or `FAIL`). The `combine` operator walks the two trees
        simultaneously and invokes your rule whenever a structural conflict occurs.
  
    - **`merge`:**
      
        This is simply a specialized alias for `combine(tree1, tree2, op=Resolver.LAST)`. It is the classic "
        right-side wins" overlay.

### N-ary Operations: Processing a Sequence of Trees

When you have a stream, list, or fleet of objects and you need to squash them into a single result, you are performing
an **N-ary Operation**.

**The Analogy:** Imagine stacking 100 transparencies on top of an overhead projector. You need a rule for how the light
passes through all of them.

- **Tools to use:**
    - **`functools.reduce` + `combine`:**
      
        Because our binary operations (like `merge` or `combine` with `NumericResolver.SUM`) are mathematically
        designed as *Monoids*, they can be chained indefinitely. You can take a list of 1,000 partial JSON
        payloads and `reduce` them into a single, structurally sound object.
  
    - **Collectors (`MappingCollector`, `CategoryCollector`):**
  
        If your stream of objects is flat (like a database cursor) and you need to *build* the tree
        structure while aggregating collisions, you use a Collector with a specified `Aggregation`
        mode (`COUNT`, `EMA`, `ALL`).

---

## 3. Dimensionality and Shape (The Tensor Model)

In data engineering, we often borrow mental models from linear algebra. `mappingtools` brings these exact concepts to
symbolic JSON data. You can think of a nested dictionary as a sparse, irregular tensor.

### Tensor Reshaping (`flatten` vs. `reshape`)

Just like `tensor.flatten()` and `tensor.reshape()` in PyTorch or NumPy, you can manipulate the "dimensions" of your
trees without losing data.

- **`flatten` (Dimensionality Reduction):**
  
    It takes an N-dimensional tree and projects it down into a **1-Dimensional
    vector space**. The "coordinates" of that space are the tuple paths (e.g., `("user", "address", "zip")`). This is
    crucial for tasks like deep diffing, as it's much easier to compare two 1D vectors than two 3D trees.

- **`reshape` (Dimensionality Expansion):**

    It takes a flat 1D stream of records (like a database cursor) and "inflates" it back into an N-dimensional tree.
    It allows you to define the "axes" of your new tensor using `keys=["country", "state", "city"]`.

### The Inverse Mapping (The Preimage)

The `inverse` operator is pure set theory.

If a dictionary is a mathematical function $f$ mapping keys to values ($f: K \rightarrow V$), then `inverse` calculates
the **preimage** ($f^{-1}: V \rightarrow \mathcal{P}(K)$).

**The Analogy:**
This is the mathematical definition of a **Search Index**.
If you have: `{"user1": {"admin"}, "user2": {"viewer"}}`, taking the `inverse` instantly gives you the lookup index:
`{"admin": {"user1"}, "viewer": {"user2"}}`.

---

## 4. The Broadcasting Functor: `Dictifier`

If `combine` is about fusing parallel structures, `Dictifier` is about **Broadcasting** (or "Vectorization").

In category theory, a `Dictifier` acts as a **Functor**. It is a container that knows how to map a function uniformly
over its contents.

When you do this:

```python
fleet = Dictifier({"worker_a": Worker(), "worker_b": Worker()})
results = fleet.do_work()
```

You are taking a method (`do_work`) that belongs to a single, inner object, and you are "broadcasting" it across the
entire outer mapping simultaneously.

**The Analogy:** It is the exact same principle as **NumPy vectorization**. In NumPy, you don't write
`for item in array: item * 2`; you simply write `array * 2`. `Dictifier` brings that exact same vectorization power to
arbitrary Object-Oriented methods over dictionaries.

It eliminates boilerplate `for` loops from your architecture, turning imperative iteration into declarative statements.
