from mappingtools.structures import Dictifier, dictify
from mappingtools.structures.dictifier import AutoDictifier


def test_dictify_decorator():
    """Test the @dictify decorator."""

    @dictify
    class GreeterCollection:
        def __init__(self, greeting: str):
            self.greeting = greeting

        def greet(self, name: str) -> str:
            return f"{self.greeting}, {name}!"

        @property
        def greeting_length(self) -> int:
            return len(self.greeting)

    items = GreeterCollection(
        {
            "english": GreeterCollection.Item("Hello"),
            "french": GreeterCollection.Item("Bonjour"),
        }
    )

    # Test method call
    greetings = items.greet("Galaxy")
    assert isinstance(greetings, Dictifier)
    assert not isinstance(greetings, AutoDictifier)
    assert greetings == {
        "english": "Hello, Galaxy!",
        "french": "Bonjour, Galaxy!",
    }

    # Test property access
    lengths = items.greeting_length
    assert isinstance(lengths, dict)
    assert lengths == {"english": 5, "french": 7}

    # Test that the subclass is a subclass of Dictifier
    assert issubclass(GreeterCollection, Dictifier)


def test_dictify_decorator_empty():
    """Test an empty collection created with the @dictify decorator."""

    @dictify
    class GreeterCollection:
        # Added return type hint to ensure strict Dictifier is returned
        def greet(self, name: str) -> str: ...

    # Create an empty collection
    items = GreeterCollection()
    assert len(items) == 0

    # Method call on empty dictifier should return an empty dictifier
    greetings = items.greet("No one")
    assert isinstance(greetings, Dictifier)
    assert not isinstance(greetings, AutoDictifier)
    assert not greetings
