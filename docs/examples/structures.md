---
icon: lucide-braces
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

## dictify

A class decorator that transforms a class definition into a specialized `Dictifier` collection.

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

## AutoDictifier

A flexible subclass of `Dictifier` that automatically infers the type of its contents.

<!-- name: test_auto_dictifier_inference -->
```python linenums="1"
from mappingtools.structures import AutoDictifier

class User:
    def __init__(self, name: str):
        self.name = name
    
    def greet(self):
        return f"Hi, I'm {self.name}"

# No type hint needed
users = AutoDictifier({
    "u1": User("Alice"),
    "u2": User("Bob"),
})

# It infers 'User' and allows method calls
greetings = users.greet()
print(greetings)
# output: {'u1': "Hi, I'm Alice", 'u2': "Hi, I'm Bob"}
```
