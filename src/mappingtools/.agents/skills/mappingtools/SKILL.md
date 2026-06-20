---
name: mappingtools
description: >
  A Python library for advanced, composable manipulation of nested data structures (trees).
  Use for tasks involving data transformation, configuration management, ETL, and architectural patterns.
  It excels at deep merging, reshaping, patching, and broadcasting operations on JSON-like objects.
---

## Mental Model

The library operates on a **Recursive Tree** structure (like JSON) and classifies all operations into three categories:

1.  **Unary Operations (Transforming a Single Tree):** Use `transformers` (like `strictify`, `minify`) for recursive content changes and `optics.Lens` for surgical, immutable modifications.
2.  **Binary Operations (Fusing Two Trees):** Use `operators.combine` or `operators.merge` to fuse two trees with explicit conflict resolution.
3.  **N-ary Operations (Processing a Sequence of Trees):** Use `collectors` (like `MappingCollector`, `CategoryCollector`) to build a tree from a flat stream, or `functools.reduce` with `combine` to fold a list of trees into one.

## Core Use Cases & Recipes

### Configuration Management with Conflict Resolution
Merge multiple configuration layers and handle conflicts explicitly.

```python
from functools import reduce
from mappingtools.operators import combine
from mappingtools.resolvers import NumericResolver

# Use combine with a SUM resolver for numeric conflicts
tree1 = {"a": 1, "b": {"c": 10}}
tree2 = {"a": 2, "b": {"c": 20}, "d": 5}
summed = combine(tree1, tree2, op=NumericResolver.SUM)
# -> {'a': 3, 'b': {'c': 30}, 'd': 5}
```

### Advanced Data Reshaping (ETL)
Convert a flat list of records into a multi-dimensional "tensor" and aggregate values.

```python
from mappingtools.operators import reshape
from mappingtools.aggregations import Aggregation

data = [
    {"country": "US", "state": "NY", "city": "NYC", "pop": 8.4},
    {"country": "US", "state": "CA", "city": "LA", "pop": 3.9},
    {"country": "UK", "state": "ENG", "city": "LON", "pop": 8.9},
    {"country": "US", "state": "NY", "city": "Albany", "pop": 0.1},
]

# Sum population by Country -> State
state_pop = reshape(
    data, 
    keys=["country", "state"], 
    value="pop", 
    aggregation=Aggregation.SUM
)
# -> {'US': {'NY': 8.5, 'CA': 3.9}, 'UK': {'ENG': 8.9}}
```

### Broadcasting with Deep Proxying
Apply a method or access an attribute across a collection of objects simultaneously, without a `for` loop.

```python
from mappingtools.structures import Dictifier

class Address:
    def __init__(self, city: str): self.city = city
class User:
    address: Address
    def __init__(self, name: str, city: str): self.address = Address(city)

users = Dictifier[User]({
    "u1": User("Alice", "New York"),
    "u2": User("Bob", "London"),
})

# Chain attribute access through the collection
cities = users.address.city
# -> {'u1': 'New York', 'u2': 'London'}
```

### Surgical Multi-Patching
Apply multiple, targeted, immutable updates to a complex object in one operation.

```python
from mappingtools.optics import patch

config = {
    "server": {"host": "localhost", "port": 8080},
    "db": {"name": "test"}
}

# Apply a patch with dot-separated paths
new_config = patch(config, {
    "server.host": "0.0.0.0",
    "db.name": "prod"
})
# -> {'server': {'host': '0.0.0.0', 'port': 8080}, 'db': {'name': 'prod'}}
```

## Key Modules

-   **`operators`**: Stateless functions for transforming mappings (`merge`, `flatten`, `reshape`, `inverse`, `combine`).
-   **`transformers`**: Functions for recursively reshaping the *content* of an object (`simplify`, `stringify`, `minify`, `strictify`).
-   **`collectors`**: Stateful classes for aggregating data from streams (`MappingCollector`, `CategoryCollector`, `MeteredDict`, `AutoMapper`).
-   **`structures`**: Advanced dictionary-like containers for broadcasting operations (`Dictifier`, `LazyDictifier`).
-   **`optics`**: Functional tools for immutable access and modification of nested data (`Lens`, `patch`, `project`).

## Gotchas & Best Practices

-   **Immutability by Default**: All operators return new data structures, they do not modify inputs in place. This is a core safety feature.
-   **`combine` vs `merge`**: `merge` is a simple "last-win" merge. `combine` is a powerful, generalized version that lets you specify a `Resolver` for handling conflicts (e.g., `NumericResolver.SUM`, `Resolver.FAIL`).
-   **`Dictifier` Performance**: For performance-critical synchronous code, prefer the `@dictify` decorator over the generic `Dictifier[T]`, as it pre-compiles the proxies. Async overhead is minimal.
-   **`Lens` Composition**: Build complex lenses by composing them with `/`: `Lens.key("users") / 0 / "profile" / "name"`.
-   **`strictify` vs `modify`**: `strictify` traverses into *all* objects, including class instances, converting them to dicts. `modify` treats class instances as atomic "leaf" nodes and does not traverse into them.