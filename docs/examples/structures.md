---
icon: lucide/square-code
---

# Structures

!!! Abstract
Structures are advanced, dictionary-like data structures that act as proxies or containers for collections of objects.

## Dictifier

`Dictifier` is a strict, type-safe container that proxies method calls and attribute access to a collection of objects.

<!-- name: test_dictifier_basic -->

```python linenums="1"
from mappingtools.structures import Dictifier


class Greeter:
    def __init__(self, greeting: str):
        self.greeting = greeting

    def greet(self, name: str) -> str:
        return f"{self.greeting}, {name}!"


# Create a Dictifier of Greeters
greeters = Dictifier[Greeter]({
    "english": Greeter("Hello"),
    "spanish": Greeter("Hola"),
})

# Broadcast a method call
greetings = greeters.greet("World")
print(greetings)
# output: {'english': 'Hello, World!', 'spanish': 'Hola, World!'}
```

### Auto-Inference Mode

For convenience, you can use the `Dictifier.auto()` factory to create a `Dictifier` that infers the type of its
contents.

<!-- name: test_dictifier_auto_inference -->

```python linenums="1"
from mappingtools.structures import Dictifier


class User:
    def __init__(self, name: str):
        self.name = name

    def greet(self):
        return f"Hi, I'm {self.name}"


# No type hint needed
users = Dictifier.auto({
    "u1": User("Alice"),
    "u2": User("Bob"),
})

# It infers 'User' and allows method calls
greetings = users.greet()
print(greetings)
# output: {'u1': "Hi, I'm Alice", 'u2': "Hi, I'm Bob"}
```

### Deep Proxying

`Dictifier` enables powerful, chained access to nested object attributes when type hints are present.

<!-- name: test_dictifier_deep_proxying -->

```python linenums="1"
from mappingtools.structures import Dictifier


class Address:
    def __init__(self, city: str):
        self.city = city


class User:
    address: Address  # Type hint is crucial

    def __init__(self, name: str, city: str):
        self.name = name
        self.address = Address(city)


# Create a Dictifier of Users
users = Dictifier[User]({
    "u1": User("Alice", "New York"),
    "u2": User("Bob", "London"),
})

# Accessing 'address' returns a new Dictifier
addresses = users.address

# Chain the access to get the 'city' from each Address
cities = addresses.city
print(cities)
# output: {'u1': 'New York', 'u2': 'London'}
```

### dictify

A class decorator that transforms a class definition into a specialized `Dictifier` collection with optimized
performance.

<!-- name: test_dictify_decorator -->

```python linenums="1"
from mappingtools.structures import dictify


@dictify
class UserCollection:
    # This class body defines the interface for the items.
    def __init__(self, name: str):
        self.name = name

    def greet(self):
        return f"Hi, I'm {self.name}"


# UserCollection is now a Dictifier for UserCollection.Item
users = UserCollection({
    "admin": UserCollection.Item("Admin"),
    "guest": UserCollection.Item("Guest"),
})

greetings = users.greet()
print(greetings)
# output: {'admin': "Hi, I'm Admin", 'guest': "Hi, I'm Guest"}
```

### Performance

`Dictifier` provides a lot of convenience, but this comes with some overhead compared to a native loop. The performance
characteristics depend on how you use it and the size of your collection.

!!! tip "Key Takeaways"

- **Async is cheap:** The overhead for `async` methods is very low (often <10%).
- **`@dictify` is fast:** The decorator pre-compiles proxies, making it significantly faster than the generic
  `Dictifier[T]` for synchronous code.
- **Overhead matters less on large collections:** The fixed cost of proxying is less significant as the time spent
  looping over items increases.

Below are example benchmark results.

#### Synchronous Overhead

| Collection Size | Native Loop | `Dictifier[T]` (Generic) | `@dictify` (Decorator) |
|-----------------|-------------|--------------------------|------------------------|
| 10 items        | `0.02s`     | `~300%` overhead         | `~100%` overhead       |
| 1000 items      | `0.02s`     | `~80%` overhead          | `~70%` overhead        |

#### Asynchronous Overhead

| Collection Size | Native `asyncio.gather` | `Dictifier[T]` (Async) |
|-----------------|-------------------------|------------------------|
| 10 items        | `0.7s`                  | `~18%` overhead        |
| 1000 items      | `0.6s`                  | `~8%` overhead         |

## LazyDictifier

A lazy version of `Dictifier` that defers execution until results are accessed. This is ideal for large datasets or
streaming pipelines where memory efficiency is critical.

<!-- name: test_lazy_dictifier -->

```python linenums="1"
from mappingtools.structures import LazyDictifier


class Greeter:
    def __init__(self, name: str):
        self.call_count = 0
        self.name = name

    def greet(self) -> str:
        self.call_count += 1
        return f"Hello, {self.name}!"


greeter = Greeter("Alice")
data = {"a": greeter}
lazy = LazyDictifier(data)

# Create the proxy - should NOT call greet() yet
greetings = lazy.greet()
print(f"Call count before access: {greeter.call_count}")
# output: Call count before access: 0

# Access an item - SHOULD call greet() now
print(greetings["a"])
# output: Hello, Alice!
print(f"Call count after access: {greeter.call_count}")
# output: Call count after access: 1
```

## map_objects

A factory function that provides a unified entry point for creating `Dictifier` or `LazyDictifier` instances.

<!-- name: test_map_objects -->

```python linenums="1"
from mappingtools.structures import map_objects


class User:
    def __init__(self, name: str):
        self.name = name

    def greet(self):
        return f"Hi, I'm {self.name}"


data = {"u1": User("Alice")}

# Create a strict Dictifier
strict_users = map_objects(data, type_hint=User)

# Create an auto-inferring Dictifier
auto_users = map_objects(data)

# Create a lazy Dictifier
lazy_users = map_objects(data, lazy=True)

print(f"Strict: {strict_users.greet()}")
# output: Strict: {'u1': "Hi, I'm Alice"}
print(f"Auto: {auto_users.greet()}")
# output: Auto: {'u1': "Hi, I'm Alice"}
print(f"Lazy (on access): {lazy_users.greet()['u1']}")
# output: Lazy (on access): Hi, I'm Alice
```

