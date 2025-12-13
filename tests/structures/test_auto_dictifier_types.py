from collections import namedtuple
from dataclasses import dataclass
from typing import NamedTuple

from mappingtools.structures import AutoDictifier


@dataclass
class UserData:
    name: str
    age: int

    def greet(self) -> str:
        return f"Hi, I'm {self.name}"


class SlottedUser:
    __slots__ = ("age", "name")

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"Hi, I'm {self.name}"


class TupleUser(NamedTuple):
    name: str
    age: int

    def greet(self) -> str:
        return f"Hi, I'm {self.name}"


# Functional namedtuple
FuncTupleUser = namedtuple("FuncTupleUser", ["name", "age"])


def test_auto_dictifier_dataclass():
    """Test AutoDictifier inference with dataclasses."""
    # No type hint provided!
    users = AutoDictifier({
        "u1": UserData("Alice", 30),
        "u2": UserData("Bob", 25),
    })

    # Test method access (requires correct inference)
    greetings = users.greet()
    assert greetings == {
        "u1": "Hi, I'm Alice",
        "u2": "Hi, I'm Bob",
    }

    # Test field access
    ages = users.age
    assert ages == {
        "u1": 30,
        "u2": 25,
    }


def test_auto_dictifier_slots():
    """Test AutoDictifier inference with classes using __slots__."""
    # No type hint provided!
    users = AutoDictifier({
        "u1": SlottedUser("Alice", 30),
        "u2": SlottedUser("Bob", 25),
    })

    # Test method access
    greetings = users.greet()
    assert greetings == {
        "u1": "Hi, I'm Alice",
        "u2": "Hi, I'm Bob",
    }

    # Test field access
    ages = users.age
    assert ages == {
        "u1": 30,
        "u2": 25,
    }


def test_auto_dictifier_named_tuple():
    """Test AutoDictifier inference with NamedTuples."""
    # No type hint provided!
    users = AutoDictifier({
        "u1": TupleUser("Alice", 30),
        "u2": TupleUser("Bob", 25),
    })

    # Test method access
    greetings = users.greet()
    assert greetings == {
        "u1": "Hi, I'm Alice",
        "u2": "Hi, I'm Bob",
    }

    # Test field access
    ages = users.age
    assert ages == {
        "u1": 30,
        "u2": 25,
    }


def test_auto_dictifier_functional_named_tuple():
    """Test AutoDictifier inference with namedtuple created via function."""
    # No type hint provided!
    users = AutoDictifier({
        "u1": FuncTupleUser("Alice", 30),
        "u2": FuncTupleUser("Bob", 25),
    })

    # Test field access
    ages = users.age
    assert ages == {
        "u1": 30,
        "u2": 25,
    }
